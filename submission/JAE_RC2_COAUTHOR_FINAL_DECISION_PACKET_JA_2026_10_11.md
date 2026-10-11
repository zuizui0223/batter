# JAE v0.4.0 — 共著者・責任著者への最終確認パケット（2026-10-11）

**これは著者確認用の公開テンプレートです。著者の承認・署名・連絡先・非公開の許可文書を、この公開リポジトリに記録しないでください。** 現時点で承認が得られたという意味ではありません。

## 論文・バージョン

- 対象：*Persistent individual vertical strategies need not partition three-dimensional space in two tropical bat species*
- 科学的原稿：`release/jae-v0.4.0-rc2`、`manuscript/MANUSCRIPT_DRAFT_V0_4_0.md`、Git blob `c4ef51a7f3f291a6f203d303dbf73f5b54fb7683`。
- 研究結論：共通の水平空間と高度オフセットを考慮しても個体性が残り、対象2種の4パネルでは地形相対の鉛直利用が持続。追加的な正の空間分離は4/4で支持なし。ただし**ゼロ分離を証明したわけではない**。同時利用の検証には2023年の例外あり。
- 投稿形式・図・匿名原稿は旧RC2で検証済みだが、**人間の実際の著者情報・新しいAI開示・正式アーカイブDOIを加えた最終版では未検証**。
- Draft PR：[#97](https://github.com/zuizui0223/batter/pull/97)。

## 著者が判断・確認すべき6点

1. **著者と責任**：共著者全員が最終原稿と著者順を確認したか。各人の所属、ORCID、CRediT役割、責任著者、利益相反、研究費、謝辞について合意したか。著者名・連絡先は適切な非公開経路で管理する。
2. **生成AI利用**：実際にChatGPT等を用いた範囲は何か（文章案、研究設計、解析スクリプト作成・デバッグ、文献点検など）。人間が実施したデータ・コード・主張の照合は何か。単なる文法校正だったと虚偽申告せず、実質的使用ならMethodsまたはAcknowledgementsの正確な開示段落を承認する。未確認の検証実施を主張しない。
3. **包摂性・地域との関わり**：公開データを採集した地域の研究者・関係者との実際の協働、文献・謝辞、意見表明の機会を、事実に基づきJAE提出欄に記載する。行っていない活動を作らない。
4. **元データの権利と帰属**：主解析6 DOI・外部検証4 DOIの原著引用、公開ライセンス、機密性の高い野生動物位置情報を確認する。DataCite上は9件CC0、*Nyctalus* Zenodo 1件CC BY 4.0。原著の提供条件・著者への連絡や帰属要件を**各DOIで**最終確認する。公開DOIがあるだけで全ての二次配布を自動許可としない。
5. **新規解析コードのライセンス**：新たに作成したリポジトリのプログラムについて、権利者が適切なソフトウェアライセンスを1つ決める。原データ10件のライセンスとは混同しない。
6. **公開と投稿の最終版**：生成AI開示により原稿が変わるなら、凍結済みRC2を直接書き換えず、承認済み開示段落のみを加えた別版候補を作成。投稿規定の字数、匿名査読PDF、Supporting Information、ソースコードの再現性を再検証。必要なZenodoの実際のバージョンDOI取得後に最終ゲートを通し、責任著者がJAEに投稿する。

## 合意内容の記録先

公開テンプレートは内容やチェック条件の型を定めるためだけのものです。**記録されていない承認は、承認されたと扱いません。**

- 著者メタデータ形式：`submission/jae_v0_4_0_metadata.template.json`
- JAE包摂性・AI使用・人間の責任に関する条件：`submission/jae_v0_4_0_policy_signoff.template.json`
- 原データ10 DOIの権利確認形式：`submission/jae_v0_4_0_original_source_rights.template.json`
- DataCite登録ライセンスの証拠：`submission/JAE_RC2_EXECUTED_TEN_SOURCE_DATACITE_RIGHTS_RESULT_2026_10_10.md`
- 生成AIを明示した原稿へ移行するルール：`submission/JAE_RC2_TO_VERSIONED_AI_DISCLOSURE_CANDIDATE_CONTRACT_V1.md`
- 投稿前の統合検査：`python scripts/check_jae_v0_4_0_integrated_final_editorial_gate.py --strict`

### 現在地と停止条件

現実の著者メタデータ、共同著者による内容・AI使用範囲の承認、個別データ所有者の権利確認、ソフトウェアライセンス、正式版DOIが未承認・未取得の状態では**投稿保留**です。Green CIは、こうしたHOLDが正しく働くという意味です。

すべて揃っても、**著者による最終原稿の熟読と投稿先への提出は別の人間の行為**です。AIや自動スクリプトはこれらの責任を代行しません。
