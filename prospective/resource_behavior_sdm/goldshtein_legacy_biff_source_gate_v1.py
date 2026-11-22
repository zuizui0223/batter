"""Source-hash-locked OLE2/BIFF8 structural reader for legacy Goldshtein .xls.

Pure Python stdlib; no Excel execution, no raw cactus IDs/coordinates output.
Supports this pinned upload and rejects unknown SST/BIFF layouts, rather than
pretending to be a general XLS importer. Uploaded checksum != publisher proof.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timedelta
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
import zipfile

ZIP_SHA = "069b12e6383fa7d84a1f7164fcfe16b0ce693469a7661262ce1a0ed73e423ebb"
XLS_SHA = "459b3d838b56ed465bcddf495565b03ced421ae9b7b45a9d1425658f0cad7b6c"
XLS_NAME = "open flowers.xls"


def rk_number(rk):
    i = struct.unpack("<i", struct.pack("<I", rk))[0] >> 2
    v = float(i) if rk & 2 else struct.unpack("<d", b"\0" * 4 + struct.pack("<I", rk & ~3))[0]
    return v / 100.0 if rk & 1 else v


def _stream(blob):
    if blob[:8] != bytes.fromhex("d0cf11e0a1b11ae1") or len(blob) > 300000:
        raise ValueError("STOP_NOT_PINNED_OLE2_XLS")
    sector = 1 << struct.unpack_from("<H", blob, 30)[0]
    if sector != 512:
        raise ValueError("STOP_UNSUPPORTED_OLE_SECTOR")
    nfat = struct.unpack_from("<I", blob, 44)[0]
    if not 0 < nfat < 64:
        raise ValueError("STOP_OLE_FAT_SIZE")
    ids = struct.unpack_from("<109I", blob, 76)[:nfat]
    fat = []
    for idx in ids:
        fat.extend(struct.unpack_from("<128I", blob, 512 + idx * sector))

    def readchain(idx, size=None):
        chunks, seen = [], set()
        while idx not in (0xFFFFFFFE, 0xFFFFFFFF):
            if idx >= len(fat) or idx in seen or len(seen) > 1000:
                raise ValueError("STOP_UNSAFE_OLE_SECTOR_CHAIN")
            seen.add(idx)
            chunks.append(blob[512 + idx * sector:512 + (idx + 1) * sector])
            idx = fat[idx]
        output = b"".join(chunks)
        return output[:size] if size is not None else output

    directory = readchain(struct.unpack_from("<I", blob, 48)[0])
    streams = []
    for at in range(0, len(directory), 128):
        entry = directory[at:at + 128]
        if len(entry) < 128:
            continue
        length = struct.unpack_from("<H", entry, 64)[0]
        if not 2 <= length <= 64 or entry[66] != 2:
            continue
        name = entry[:length - 2].decode("utf-16le")
        streams.append((name, struct.unpack_from("<I", entry, 116)[0],
                        struct.unpack_from("<Q", entry, 120)[0]))
    workbooks = [item for item in streams if item[0] == "Workbook"]
    if len(workbooks) != 1 or not 4096 < workbooks[0][2] < 300000:
        raise ValueError("STOP_UNEXPECTED_BIFF_WORKBOOK_STREAM")
    return readchain(workbooks[0][1], workbooks[0][2])


def read_pinned_source_tables(blob):
    if sha256(blob).hexdigest() != XLS_SHA:
        raise ValueError("STOP_LEGACY_XLS_SHA_MISMATCH")
    book = _stream(blob)
    records, at = [], 0
    while at + 4 <= len(book):
        typ, length = struct.unpack_from("<HH", book, at)
        if at + 4 + length > len(book):
            raise ValueError("STOP_BIFF_RECORD_OVERFLOW")
        records.append((at, typ, book[at + 4:at + 4 + length]))
        at += 4 + length
        if len(records) > 15000:
            raise ValueError("STOP_BIFF_TOO_MANY_RECORDS")
    sst, sheets = [], []
    for i, (pos, typ, data) in enumerate(records):
        if typ == 0x85:
            off, _state, kind, n, flag = struct.unpack_from("<IBBBB", data)
            name = data[8:8 + 2 * n].decode("utf-16le") if flag & 1 else data[8:8 + n].decode("latin1")
            if kind == 0:
                sheets.append((off, name))
        elif typ == 0xFC:
            if i + 1 < len(records) and records[i + 1][1] == 0x3C:
                raise ValueError("STOP_UNSUPPORTED_SPLIT_BIFF_SST")
            _total, unique = struct.unpack_from("<II", data)
            pointer = 8
            for _ in range(unique):
                if pointer + 3 > len(data):
                    raise ValueError("STOP_BIFF_BAD_SST")
                count, flags = struct.unpack_from("<HB", data, pointer)
                pointer += 3
                if flags & 12:
                    raise ValueError("STOP_UNSUPPORTED_RICH_BIFF_STRING")
                size = count * (2 if flags & 1 else 1)
                if pointer + size > len(data):
                    raise ValueError("STOP_BIFF_BAD_STRING_SPAN")
                sst.append(data[pointer:pointer + size].decode("utf-16le" if flags & 1 else "latin1"))
                pointer += size
    if sorted(name for pos, name in sheets) != ["1-6-2016", "Sheet1"]:
        raise ValueError("STOP_BIFF_WRONG_SHEET_LAYOUT")
    result = {}
    for start, name in sheets:
        stop = min([pos for pos, _name in sheets if pos > start] + [len(book)])
        cells = {}
        for pos, typ, data in records:
            if not start <= pos < stop or len(data) < 4:
                continue
            if typ == 0xFD:
                row, col, _xf, index = struct.unpack_from("<HHHI", data)
                if index >= len(sst):
                    raise ValueError("STOP_BAD_BIFF_STRING_INDEX")
                cells[row, col] = sst[index]
            elif typ == 0x203:
                row, col, _xf, value = struct.unpack_from("<HHHd", data)
                cells[row, col] = value
            elif typ == 0x27E:
                row, col, _xf, packed = struct.unpack_from("<HHHI", data)
                cells[row, col] = rk_number(packed)
            elif typ == 0xBD:
                row, firstcol = struct.unpack_from("<HH", data)
                lastcol = struct.unpack_from("<H", data, len(data) - 2)[0]
                pointer = 4
                for col in range(firstcol, lastcol + 1):
                    if pointer + 6 > len(data) - 2:
                        raise ValueError("STOP_MALFORMED_MULRK")
                    _xf, packed = struct.unpack_from("<HI", data, pointer)
                    cells[row, col] = rk_number(packed)
                    pointer += 6
        result[name] = cells
    return result


def source_summary_from_zip(source_zip):
    file = Path(source_zip)
    digest = sha256()
    with file.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    if digest.hexdigest() != ZIP_SHA:
        raise ValueError("STOP_ORIGINAL_ZIP_SHA_MISMATCH")
    with zipfile.ZipFile(file) as archive:
        tables = read_pinned_source_tables(archive.read(XLS_NAME))
    flowers, ground = tables["Sheet1"], tables["1-6-2016"]
    if [flowers.get((0, col)) for col in range(10)] != [
            "year", "source", "startDate", "cactus", "branch", "buds",
            "young", "fruits", "lat", "lon"]:
        raise ValueError("STOP_SOURCE_FLORAL_HEADER_CHANGED")
    if [ground.get((0, col)) for col in range(4)] != [
            "num", "lat", "lon", "alt"]:
        raise ValueError("STOP_SOURCE_DRONE_GROUND_HEADER_CHANGED")
    source_counts, number_counts = Counter(), Counter()
    dates, monitored, positive = set(), set(), 0
    base = datetime(1899, 12, 30)
    for row in range(1, 415):
        kind, start, year = (flowers.get((row, col)) for col in (1, 2, 0))
        if not isinstance(start, (float, int)) or year not in (2015, 2016, 2017):
            raise ValueError("STOP_INVALID_EXCEL_START_DATE_OR_YEAR")
        source_counts[kind] += 1
        for day in range(1, 18):
            value = flowers.get((row, day + 9))
            if not isinstance(value, (float, int)):
                continue
            if not math.isfinite(value) or value < 0:
                raise ValueError("STOP_INVALID_SOURCE_FLOWER_NUMBER")
            number_counts[kind] += 1
            positive += value > 0
            if kind == "drone 30m":
                monitored.add(row)
                dates.add((base + timedelta(days=start + day - 1)).date())
    expected = Counter({
        "drone 30m": 327, "Saguaral": 48, "exp. 2": 23,
        "US border": 10, "Tecolote": 6})
    if source_counts != expected or len({row for row, col in ground if row > 0}) != 332:
        raise ValueError("STOP_ORIGINAL_414_CACTUS_OR_332_DRONE_STRUCTURE_DRIFT")
    return {
        "schema": "batter.goldshtein_legacy_BIFF8_source_structural_receipt.v1",
        "source_original_zip_sha256": ZIP_SHA,
        "legacy_xls_sha256": XLS_SHA,
        "n_legacy_workbook_sheets": 2,
        "n_source_cacti": sum(source_counts.values()),
        "source_categories": dict(source_counts),
        "n_drone_cacti": 327,
        "n_drone_cacti_with_numeric_daily_count": len(monitored),
        "n_drone_cacti_without_numeric_daily_count": 327 - len(monitored),
        "n_original_numeric_day_cells": sum(number_counts.values()),
        "n_original_numeric_positive_day_cells": int(positive),
        "n_drone_numeric_day_cells": number_counts["drone 30m"],
        "n_drone_candidate_date_labels": len(dates),
        "mean_recorded_days_per_monitored_drone_cactus": number_counts["drone 30m"] / len(monitored),
        "n_second_sheet_ground_altitude_points": 332,
        "numbered_columns_as_calendar_days_not_independently_verified": True,
        "unmeasured_days_not_imputed_zero": True,
        "does_not_export_source_geographic_or_bat_cactus_identifiers": True,
        "biological_resource_height_effect": None,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("original_source_zip")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    Path(args.out).write_text(
        json.dumps(source_summary_from_zip(args.original_source_zip), indent=2) + "\n",
        encoding="utf-8")
    print("ORIGINAL_LEGACY_SOURCE_STRUCTURALLY_AUDITED_ONLY")
