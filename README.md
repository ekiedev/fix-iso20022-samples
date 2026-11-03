# FIX protocol, SWIFT MT940 and ISO 20022 sample files

Free, **synthetic** test files for anyone building or debugging FIX engines, bank-statement imports, treasury/ERP connectors or payment-file generators:

- **FIX logs** — a FIX 4.4 order session in QuickFIX-style log format, the same session as raw SOH-delimited messages, a set of session- and business-level rejects (`35=3`, `35=j`, `35=9`, rejected `35=8`), a FIX 4.2 equity session and a FIXT.1.1 / FIX 5.0 SP2 crypto session.
- **QuickFIX data dictionary** — a broker-specific custom-field overlay (tags 5000–9999 and 20000+) in QuickFIX XML format.
- **SWIFT MT940 / MT942** — customer statements with German structured `:86:` (`?20`–`?63`, `EREF+`/`SVWZ+`), slash-coded `:86:` (`/IBAN/`, `/NAME/`, `/REMI/`) and Dutch-style `/CNTP/` counterparty blocks with a direct-debit return, plus an intraday MT942.
- **ISO 20022** — `camt.053.001.02` and `camt.053.001.08` bank statements (all validate against the official XSDs), a valid `pain.001.001.09` credit-transfer file and one with typical bank-rejection errors.

All companies, references and amounts are fictitious. IBANs are the widely published example IBANs (e.g. `DE89370400440532013000`, `NL91ABNA0417164300`). Nothing here comes from a real bank or client.

## Open them in your browser — nothing is uploaded

The files are made to be dropped into two free, 100% client-side tools (no account, no upload, no tracking — verify in DevTools → Network):

- **[SafeFIX](https://biteapps.cc/safefix/)** — FIX log analyzer, QuickFIX-format XML dictionary validator, reject explainer, order-latency view and log anonymizer that recalculates `BodyLength (9)` and `CheckSum (10)`.
- **[SafeCAMT](https://biteapps.cc/safecamt/)** — camt.052/053/054 and MT940/MT942 to Excel/CSV with balance reconciliation, MT940 → camt.053 conversion, and pain.001 checks.

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

Contributions of further anonymized edge cases (odd delimiters, bank-specific `:86:` dialects, other camt/pain versions) are welcome as pull requests. Please never submit real client data.

---

Maintained by [Bite Apps](https://biteapps.cc/) — privacy-first FIX, SWIFT and ISO 20022 tools. Need a custom FIX bridge, QuickFIX dictionary help or a bank-format converter? support@biteapps.cc
