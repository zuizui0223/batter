# Official USGS sbtools documented cloud URL method; no authentication workaround.
# Do not print signed URLs, exact locations or original records.
options(timeout=180)
dir.create("nabat_sbtools_gate",showWarnings=FALSE)
dir.create("nabat_public_tables_cache",showWarnings=FALSE)
library(sbtools)
library(jsonlite)
library(httr)
item_id <- "6ace802b1ba49b69a5819e47"
sizes <- c("nabat-acoustic-data-species-list-20260925.parquet"=24922,
           "nabat-acoustic-data-manifest-20260925.parquet"=339365848,
           "nabat-acoustic-data-species-information-20260925.parquet"=330795308)
report <- list(stage="official sbtools public download route", doi="10.5066/P1HDZNY9",
               sbtools_version=as.character(packageVersion("sbtools")),
               status="START",files=list())
save_report <- function() {
  write_json(report, "nabat_sbtools_gate/report.json", auto_unbox=TRUE, pretty=TRUE, null="null")
  cat("NABAT_SBTOOLS_REPORT=",toJSON(report,auto_unbox=TRUE,null="null"),"\n",sep="")
}
save_report()
# This function is documented by USGS at https://doi-usgs.github.io/sbtools/reference/item_list_files.html
# Do not invoke authenticate(), try private cloud endpoints, or supply credentials.
tryCatch({
  stopifnot("fetch_cloud_urls" %in% names(formals(sbtools::item_list_files)))
  files <- suppressMessages(sbtools::item_list_files(item_id, fetch_cloud_urls=TRUE))
  stopifnot(all(c("fname","size","url") %in% names(files)))
  report$listed_files <- nrow(files)
  for (name in names(sizes)) {
    z <- files[files$fname==name,,drop=FALSE]
    stopifnot(nrow(z)==1, as.numeric(z$size)==sizes[[name]])
    url <- as.character(z$url)
    # Only an official library-returned HTTPS URL may be used.
    stopifnot(length(url)==1L, startsWith(url,"https://"))
    host <- httr::parse_url(url)$hostname
    stopifnot(grepl("(^|\\.)((usgs\\.gov)|(sciencebase\\.gov)|(amazonaws\\.com))$",host))
    # Verify the small file and header first; no more direct attempts if denied.
    path <- file.path("nabat_public_tables_cache",name)
    tmp <- paste0(path,".part")
    p <- GET(url, add_headers(Range="bytes=0-3","Accept-Encoding"="identity"), timeout(45))
    status <- status_code(p)
    bytes <- content(p,as="raw")
    if (status %in% c(401,403)) stop("OFFICIAL_ACCESS_STOP")
    magic <- length(bytes)>=4 && identical(bytes[1:4],charToRaw("PAR1"))
    # Range GET should be four bytes; reject unexpected large body or HTML.
    stopifnot(magic, status==206, identical(headers(p)[["content-range"]],paste0("bytes 0-3/",sizes[[name]])))
    report$files[[name]] <- list(official_host=host,range_verified=TRUE,published_size=sizes[[name]])
    save_report()
    q <- GET(url,write_disk(tmp,overwrite=TRUE),add_headers("Accept-Encoding"="identity"),timeout(600))
    if (status_code(q) %in% c(401,403)) stop("OFFICIAL_ACCESS_STOP")
    stopifnot(status_code(q)==200,file.info(tmp)$size==sizes[[name]])
    con <- file(tmp,"rb");head <- readBin(con,"raw",4);seek(con,where=-4,origin="end");tail <- readBin(con,"raw",4);close(con)
    stopifnot(identical(head,charToRaw("PAR1")),identical(tail,charToRaw("PAR1")))
    file.rename(tmp,path)
    digest <- strsplit(system2("sha256sum",shQuote(path),stdout=TRUE)," ",fixed=TRUE)[[1]][1]
    stopifnot(grepl("^[0-9a-f]{64}$",digest))
    receipt <- list(http=200,bytes_expected=sizes[[name]],source_file=name,bytes=sizes[[name]],sha256=digest,publisher_checksum_verified=NULL,official_sbtools_route=TRUE)
    write_json(receipt,paste0(path,".receipt.json"),auto_unbox=TRUE,null="null")
    report$files[[name]] <- receipt;save_report()
  }
  report$status <- "OFFICIAL_PARQUET_BYTES_READY";save_report()
},error=function(e) {
  # Avoid leaking any signed URL or response body in exception strings.
  msg <- conditionMessage(e)
  report$status <<- if (grepl("authenticat|log.?in|session|401|403|ACCESS_STOP",msg,ignore.case=TRUE)) "OFFICIAL_AUTH_OR_ACCESS_STOP" else "OFFICIAL_ROUTE_UNRESOLVED"
  report$error_class <<- class(e)[1]
  save_report()
  quit(status=1)
})
