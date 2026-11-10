# FIX, SWIFT MT940, ISO 20022, NACHA ACH and DORA sample files

Free, **synthetic** test files for anyone building or debugging FIX engines, bank-statement imports, treasury/ERP connectors, payment-file generators, ACH pipelines or DORA register-of-information reporting. Every folder has files that should pass and files with documented, planted mistakes, so you can test both sides of a validator:

- **FIX logs** — a FIX 4.4 order session in QuickFIX-style log format, the same session as raw SOH-delimited messages, a set of session- and business-level rejects (`35=3`, `35=j`, `35=9`, rejected `35=8`), a FIX 4.2 equity session and a FIXT.1.1 / FIX 5.0 SP2 crypto session.
- **QuickFIX data dictionary** — a broker-specific custom-field overlay (tags 5000–9999 and 20000+) in QuickFIX XML format.
- **SWIFT MT940 / MT942** — customer statements with German structured `:86:` (`?20`–`?63`, `EREF+`/`SVWZ+`), slash-coded `:86:` (`/IBAN/`, `/NAME/`, `/REMI/`) and Dutch-style `/CNTP/` counterparty blocks with a direct-debit return, plus an intraday MT942.
- **ISO 20022** — `camt.053.001.02` and `camt.053.001.08` bank statements (all validate against the official XSDs), a valid `pain.001.001.09` credit-transfer file and one with typical bank-rejection errors, a `pain.001` batch together with the bank's `pain.002.001.10` status report that rejects three of its payments, and `pain.008.001.08` SEPA direct debit files (valid and with planted mistakes). All validate against the official ISO 20022 XSDs.
- **NACHA ACH** — a balanced PPD / CCD / WEB origination file (LF, CR LF and no-line-break variants), the same file with nine planted mistakes (check digit, entry hash, batch and file totals, trace order, addenda sequence, missing padding, 2026 `PAYROLL` / `PURCHASE` descriptions), and a returns + notifications-of-change file (R01, R02, R03, R07, R10, C01, C02, C05).
- **DORA register of information** — a filled-in Excel register and the matching xBRL-CSV (plain-csv) reporting package for module `DORA010100`, each in a clean version and a version with planted mistakes (broken cross-template references, empty and duplicate keys, wrong LEI check digits, filing indicators, date and code formats).

All companies, people, references and amounts are fictitious. IBANs are the widely published example IBANs (e.g. `DE89370400440532013000`, `NL91ABNA0417164300`). LEIs are made-up values with correct check digits and the word EXAMPLE in them; ABA routing numbers are synthetic values that only satisfy the check-digit formula. Nothing here comes from a real bank, client or filing.

## Open them in your browser — nothing is uploaded

The files are made to be dropped into four free, 100% client-side tools (no account, no upload, no tracking — verify in DevTools → Network). Each tool also loads a built-in sample from the link in brackets:

- **[SafeFIX](https://safefix.biteapps.cc/)** ([sample](https://safefix.biteapps.cc/#sample)) — FIX log analyzer, QuickFIX-format XML dictionary validator, reject explainer, order-latency view and log anonymizer that recalculates `BodyLength (9)` and `CheckSum (10)`.
- **[SafeCAMT](https://safecamt.biteapps.cc/)** ([camt.053](https://safecamt.biteapps.cc/#camt) · [MT940](https://safecamt.biteapps.cc/#mt940) · [pain.001](https://safecamt.biteapps.cc/#pain) · [pain.001 + pain.002](https://safecamt.biteapps.cc/#pain002) · [pain.008](https://safecamt.biteapps.cc/#pain008)) — camt.052/053/054 and MT940/MT942 to Excel/CSV with balance reconciliation, MT940 → camt.053 conversion, pain.001 and pain.008 checks, pain.002 reject reports matched to the original payments, and a payment-file anonymizer that recalculates `NbOfTxs` and `CtrlSum`.
- **[SafeACH](https://safeach.biteapps.cc/)** ([origination](https://safeach.biteapps.cc/#sample) · [returns](https://safeach.biteapps.cc/#returns)) — NACHA file viewer and validator: record layouts, check digits, entry hashes, batch and file totals, return and NOC codes, plus an anonymizer that recalculates every control record.
- **[SafeDORA](https://safedora.biteapps.cc/)** ([sample](https://safedora.biteapps.cc/#sample)) — DORA register of information validator (ESA technical checks, keys and references across the 15 templates, EBA validation rules) and Excel → xBRL-CSV package builder.

Reference pages that go with the files: [FIX tags & message types](https://safefix.biteapps.cc/fix-tags/) · [FIX reject reason codes](https://safefix.biteapps.cc/fix-reject-codes/) · [MT940 format](https://safecamt.biteapps.cc/mt940-format/) · [pain.002 status & reason codes](https://safecamt.biteapps.cc/pain-002-reason-codes/) · [NACHA file format](https://safeach.biteapps.cc/nacha-file-format/) · [ACH return & NOC codes](https://safeach.biteapps.cc/ach-return-codes/) · [DORA RoI templates & fields](https://safedora.biteapps.cc/templates/) · [DORA validation rules](https://safedora.biteapps.cc/validation-rules/)

## Files

### `fix/`

| File | What it contains | What a validator should find |
|---|---|---|
| [`quickfix-session.log`](fix/quickfix-session.log) | QuickFIX-style log (`YYYYMMDD-HH:MM:SS.ffffff : 8=FIX.4.4|…`), mostly `|`-delimited with two `^A` lines: logon, NewOrderSingle, partial fill, cancel/replace, fill, a 35=3 reject, a credit-limit rejected order, cancel, market-data request answered with 35=j, heartbeats. Two non-FIX engine event lines. | 20 messages; user-defined tags 5001 and 7777 not in standard FIX 4.4; **one heartbeat with a deliberately wrong CheckSum (10=000)**; 3 rejects. |
| [`raw-soh.fix`](fix/raw-soh.fix) | The same 20 messages, raw SOH (`\x01`) delimiters, no prefixes, all BodyLength/CheckSum values correct. | Every message passes 9/10 checks. |
| [`reject-cases.log`](fix/reject-cases.log) | One NewOrderSingle per `SessionRejectReason (373)` — 0 invalid tag, 1 required tag missing, 4 empty value, 5 value out of range, 6 wrong data format — each followed by the counterparty's 35=3; plus a rejected order (35=8, 103=1), an Order Cancel Reject (35=9) and a Business Message Reject (35=j, 380=3). | Each rejected message really contains the problem named in its reject. |
| [`fix42-equity-session.log`](fix/fix42-equity-session.log) | FIX 4.2 equity session (`8=FIX.4.2`): orders with HandlInst (21), Rule80A (47) and ExecTransType (20); New → partial (150=1) → filled (150=2); cancel request → pending cancel (150=6) → cancelled (150=4); heartbeats and logout. | 15 messages, all valid against the FIX 4.2 dictionary; 2 order chains. |
| [`fixt11-fix50sp2-session.log`](fix/fixt11-fix50sp2-session.log) | FIXT.1.1 transport with FIX 5.0 SP2 application messages (`1137=9` DefaultApplVerID on Logon): crypto order with two trade fills (150=F), a second order rejected for insufficient balance; Username (553) / Password (554) on Logon for anonymizer tests. | 10 messages, no structural errors; 1 rejected order (39=8, 103=3). |

Checksums: `BodyLength (9)` counts the bytes after `9=…<SOH>` up to and including the SOH before `10=`; `CheckSum (10)` is the byte sum from `8=` through that SOH, mod 256, as three digits — computed with SOH as one byte even where the log shows `|` or `^A`.

### `dictionaries/`

| File | What it contains | How to use it |
|---|---|---|
| [`acme-prime-fix44-custom-fields.xml`](dictionaries/acme-prime-fix44-custom-fields.xml) | QuickFIX DataDictionary overlay for a fictional prime broker: custom fields 5001–5020 and 20001 with types and enums (StrategyID, AlgoUrgency, LPRoutingMode, SelfMatchPrevention…). | Load on top of FIX 4.4 (in SafeFIX: Dictionary → **+ Custom XML**) and tag 5001 in `fix/quickfix-session.log` stops being reported as UserDefined. For QuickFIX/J or QuickFIX/n, merge the `<field>` entries into your full `FIX44.xml` and add them to the relevant `<message>` definitions. |

### `swift-mt/`

| File | What it contains | Balances |
|---|---|---|
| [`mt940-german-structured-86.sta`](swift-mt/mt940-german-structured-86.sta) | MT940 with SWIFT block headers, German GVC codes (166, 191, 105, 805) and `?20…?32` subfields with `EREF+`, `MREF+`, `SVWZ+`. CRLF line endings. | `:60F:` 48,210.55 + 12,650.00 − 9,220.40 = `:62F:` 51,640.15 |
| [`mt940-slash-coded-86.sta`](swift-mt/mt940-slash-coded-86.sta) | MT940 without block headers, `:86:` in slash-code style (`/TRTP/…/IBAN/…/BIC/…/NAME/…/REMI/USTD//…/EREF/…`). | 15,200.00 + 1,250.00 − 499.75 = 15,950.25 |
| [`mt940-cntp-style-86.sta`](swift-mt/mt940-cntp-style-86.sta) | Dutch-bank-style MT940 (IBAN+currency in `:25:`, `/TRCD/` supplementary lines). `:86:` with `/EREF/`, `/CNTP/IBAN/BIC/name/city/`, `/MARF/` + `/CSID/` for a SEPA direct debit, `/REMI/USTD//` free text and `/REMI/STRD/ISO/` RF creditor reference, and a direct-debit return `/RTRN/MD06/`. Style modelled on public bank format guides; not a real bank file. | 8,450.40 + 2,952.75 − 1,792.75 = 9,610.40 |
| [`mt942-intraday.sta`](swift-mt/mt942-intraday.sta) | MT942 interim report with `:34F:`, `:13D:`, `:90D:`/`:90C:`. | No opening/closing balance (intraday). |

### `iso20022/`

| File | What it contains | Notes |
|---|---|---|
| [`camt.053.001.02-statement.xml`](iso20022/camt.053.001.02-statement.xml) | The older camt.053 version many German, Swiss and Austrian banks still deliver: PRCD/CLBD/CLAV balances, `TxsSummry`, a SEPA credit with RF reference, a SEPA direct debit with mandate ID, an outgoing transfer and a fee entry with German `Prtry` codes (`NTRF+166`, `NDDT+105`). | Valid against the official camt.053.001.02 XSD; reconciles: 25,000.00 + 3,450.00 − 8,933.40 = 19,516.60. |
| [`camt.053.001.08-statement.xml`](iso20022/camt.053.001.08-statement.xml) | End-of-day statement: PRCD/CLBD/CLAV balances, SEPA credits with structured `RF` creditor reference, a batch debit with two `TxDtls`, a SEPA direct debit, a fee entry. | Valid against the camt.053.001.08 XSD; reconciles to the cent. |
| [`camt.053.001.08-converted-from-mt940.xml`](iso20022/camt.053.001.08-converted-from-mt940.xml) | The German MT940 above converted to camt.053.001.08 (`:60F:`→OPBD, `:61:`→Ntry, `:86:`→TxDtls, `:62F:`→CLBD, `:64:`→CLAV). | Valid against the XSD. Shows a typical MT940→camt mapping; your bank's own mapping may differ in detail. |
| [`pain.001.001.09-valid.xml`](iso20022/pain.001.001.09-valid.xml) | SEPA credit transfer, two payments, structured addresses, one `RF` reference. | Counts, control sums, IBANs and SEPA rules all consistent. |
| [`pain.001.001.09-with-errors.xml`](iso20022/pain.001.001.09-with-errors.xml) | Four payments with planted problems. | EUR amount with 3 decimals; IBAN with a wrong check digit (AC01); creditor name over 70 characters; duplicate EndToEndId (AM05); `CtrlSum` that does not match (AM10); one unstructured address (AdrLine only). |
| [`pain.001.001.09-batch-answered-by-pain002.xml`](iso20022/pain.001.001.09-batch-answered-by-pain002.xml) | A SEPA credit-transfer batch of four payments (`MsgId` `PAYRUN-2026-11-05`) whose counts and control sums are right. | Two things a validator can see before sending: an IBAN with wrong check digits (payment 3) and an `EndToEndId` used twice (payments 3 and 4), plus a creditor name over 70 characters. |
| [`pain.002.001.10-status-report.xml`](iso20022/pain.002.001.10-status-report.xml) | The bank's answer to that batch: `GrpSts` and `PmtInfSts` `PART`, one `TxInfAndSts` per payment with `OrgnlEndToEndId` and, for the rejects, `OrgnlTxRef` with amount and creditor account. | Payment 1 `ACCP`; payment 2 `RJCT` `AC04` (closed account — not visible in the file); payment 3 `RJCT` `AC01` (the IBAN typo); payment 4 `RJCT` `AM05` (duplicate). The two statuses that share `EndToEndId` `SUP-90003` can only be told apart by the amount in `OrgnlTxRef`. |
| [`pain.008.001.08-valid.xml`](iso20022/pain.008.001.08-valid.xml) | SEPA Core direct debit batch (`CORE`, `RCUR`), four collections with mandate ID and signature date, creditor identifier `DE98ZZZ09999999999` at batch level, IBAN-only (`DbtrAgt` = `NOTPROVIDED`). | Counts, control sums, IBANs, creditor identifier check digits and mandate data all consistent. |
| [`pain.008.001.08-with-errors.xml`](iso20022/pain.008.001.08-with-errors.xml) | The same kind of batch with planted problems. | Creditor identifier with wrong check digits (`DE97…`, CH11); a mandate without `DtOfSgntr` (MD02); a mandate signed in the future; a debtor IBAN with a wrong check digit (AC01); `MndtId` ending in `/`; `CtrlSum` 289.60 instead of 289.65 (AM10); characters outside the SEPA set in a name (`ü`, `&`, `ö`) and in the remittance text (`–`, `ä`). |

### `ach/`

NACHA files are fixed-width: every record is exactly 94 characters, and files are padded with records of 94 nines to a multiple of 10 records. The files below were generated by [`generate_samples.py`](ach/generate_samples.py), which computes every check digit, entry hash, total and block count itself from the NACHA specification.

| File | What it contains | What a validator should find |
|---|---|---|
| [`nacha-ppd-ccd-web-valid.ach`](ach/nacha-ppd-ccd-web-valid.ach) | One file, three batches: PPD payroll credits (`PAYROLL`, checking and savings, one prenote), CCD vendor payments each with an `05` addenda record (`RMR*IV*…`), and WEB consumer debits (`PURCHASE`, Payment Type Code `S` / `R`). 11 entries, 2 addenda, 30 records including 9 padding records. LF line endings. | No errors or warnings. File totals: debits $204.49, credits $28,911.15; entry/addenda count 13; entry hash `0078800390`; block count 3. |
| [`nacha-valid-crlf.ach`](ach/nacha-valid-crlf.ach) | The same file with CR LF line endings. | Identical result. |
| [`nacha-valid-no-line-breaks.ach`](ach/nacha-valid-no-line-breaks.ach) | The same 30 records as one 2,820-character line, the way some mainframe transfers deliver them. | Identical result once the stream is cut into 94-character records. |
| [`nacha-with-errors.ach`](ach/nacha-with-errors.ach) | The valid file with nine planted mistakes. | (1) entry on line 5: routing number `053001125` fails the ABA check digit (should end in 4); (2) batch 1 control: total credit $100.00 higher than its entries; (3) lines 3–4: trace numbers not ascending; (4) batch 1: PPD wage credits described `SALARY` instead of `PAYROLL`; (5) batch 2 control: entry hash off by one; (6) line 14: addenda sequence number `0002` on the only addenda record; (7) batch 3: WEB purchase debits described `ONLINE ORD` instead of `PURCHASE`; (8) file control: entry/addenda count 12 instead of 13; (9) no padding records — 21 records instead of 30. |
| [`nacha-returns-and-noc.ach`](ach/nacha-returns-and-noc.ach) | What the originator gets back from the receiving side: two return batches (PPD, WEB) with `99` addenda records — R03 no account, R02 account closed, R01 insufficient funds, R10 not authorized, R07 authorization revoked — and a `COR` batch with `98` addenda records: C01 corrected account number, C02 corrected routing number, C05 corrected transaction code. Each addenda record carries the original entry's trace number and RDFI. | Structurally valid; 5 returns ($4,869.49 in total) and 3 notifications of change with their corrected data decoded. |

Since 20 March 2026 the Nacha rules require the Company Entry Description `PAYROLL` for PPD credits that pay wages and `PURCHASE` for e-commerce purchase debits — mistakes 4 and 7 are there to test that check.

### `dora/`

The register of information that financial entities report under Article 28(3) of DORA (Regulation (EU) 2022/2554, ITS (EU) 2024/2956), for the EBA reporting framework 4.0 module `DORA010100`. The fictional group is a German credit institution with a payment-institution subsidiary, an intra-group IT company, one branch, four contractual arrangements and three ICT third-party providers. The clean files use reference date 2025-12-31.

| File | What it contains | What a validator should find |
|---|---|---|
| [`dora-register-valid.xlsx`](dora/dora-register-valid.xlsx) | Excel register: one sheet per template (`B_01.01` … `B_99.01`), header rows with the field names and column codes, drop-down lists with the EBA closed-list values. 40 data rows across all 15 templates. | Nothing: all keys filled and unique, all 22 cross-template references resolve, all LEIs pass ISO 17442. |
| [`dora-register-with-errors.xlsx`](dora/dora-register-with-errors.xlsx) | The same register (reference date 2026-12-31) with typical spreadsheet mistakes. | One mistyped LEI in `B_01.02` (wrong check digits) that breaks the references from `B_04.01` and `B_06.01` — the kind of error that gets a whole file rejected; `ICT security` typed instead of the closed-list value `ICT security management services` in `B_05.02`; a subsequent arrangement without its overarching arrangement in `B_02.01`; an annual expense without a currency in `B_05.01`; a critical function without reasons in `B_06.01`; a not-substitutable provider without a reason in `B_07.01`. |
| [`529900EXAMPLEBANK143.CON_DE_DORA010100_DORA_2025-12-31_20260313093000000.zip`](dora/529900EXAMPLEBANK143.CON_DE_DORA010100_DORA_2025-12-31_20260313093000000.zip) | The clean register as an xBRL-CSV (plain-csv) reporting package: `META-INF/reportPackage.json`, `reports/report.json`, `parameters.csv`, `FilingIndicators.csv` and one CSV per template with EBA codes (`eba_CO:x1`, `eba_GA:DE` …). | Passes the file-name, package-structure, parameter, filing-indicator, key and reference checks. |
| [`529900EXAMPLEBANK143.CON_DE_DORA010100_DORA_2025-12-31_20260316101500000.zip`](dora/529900EXAMPLEBANK143.CON_DE_DORA010100_DORA_2025-12-31_20260316101500000.zip) | The same package with seven planted mistakes. | (1) `parameters.csv`: `refPeriod` 2025-12-30 does not match the file name; (2) `FilingIndicators.csv`: `B_03.03` declared `false`; (3) `b_01.03.csv`: empty key field (and the branch code in `b_04.01.csv` no longer resolves); (4) `b_02.01.csv`: duplicate key `CA-2023-0001`; (5) `b_02.02.csv`: a provider code that does not exist in `b_03.02.csv` / `b_05.01.csv` and fails the LEI check; (6) `b_05.02.csv`: `eba_TA:S99` is not in the closed list; (7) `b_06.01.csv`: a date written `28/11/2025` instead of `2025-11-28`. |

These files were built and checked with SafeDORA and follow the structure of the sample package the ESAs published for the register. They have not been submitted to a competent authority — use them to test your own tooling, not as proof of what a particular authority accepts.

## MT940 → camt.053 field mapping (cheat sheet)

| MT940 | camt.053 |
|---|---|
| `:20:` | `GrpHdr/MsgId`, `Stmt/Id` |
| `:25:` | `Stmt/Acct/Id/IBAN` (or `Othr/Id`) |
| `:28C:` | `ElctrncSeqNb` / `LglSeqNb` |
| `:60F:` / `:60M:` | `Bal` OPBD (or PRCD) / ITBD |
| `:61:` | `Ntry` — `ValDt`, `BookgDt`, `CdtDbtInd`, `RvslInd`, `Amt`, `BkTxCd`, `AcctSvcrRef` |
| `:86:` | `NtryDtls/TxDtls` — `Refs/EndToEndId`, `RltdPties`, `RltdAgts`, `RmtInf`; `AddtlNtryInf` |
| `:62F:` / `:62M:` | `Bal` CLBD / ITBD |
| `:64:` / `:65:` | `Bal` CLAV / FWAV |

## License

[CC0 1.0](LICENSE) — public domain. Use the files in tests, docs, demos and products without attribution.

Contributions of further anonymized edge cases (odd delimiters, bank-specific `:86:` dialects, other camt/pain versions, more pain.002 reason codes, other SEC codes, further register scenarios) are welcome as pull requests. Please never submit real client data.

---

Maintained by [Bite Apps](https://biteapps.cc/) — privacy-first FIX, SWIFT, ISO 20022, NACHA and DORA tools. Need a custom FIX bridge, QuickFIX dictionary help, a bank-format converter or help with a DORA register? support@biteapps.cc
