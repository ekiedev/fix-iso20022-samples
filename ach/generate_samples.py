#!/usr/bin/env python3
"""Generates the synthetic NACHA ACH sample files of github.com/ekiedev/fix-iso20022-samples (folder ach/).
Written from the NACHA file specification, independently of any validator: every control total, entry hash,
check digit and block count below is computed here. All names, accounts and companies are fictitious."""
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'ach')


def cd(r8):
    """ABA check digit: weights 3,7,1 over the first eight digits."""
    s = sum(int(d) * w for d, w in zip(r8, [3, 7, 1, 3, 7, 1, 3, 7]))
    return str((10 - s % 10) % 10)


def R(r8): return r8 + cd(r8)
def A(s, n): return str(s)[:n].ljust(n)      # alphanumeric: left-justified, space-filled
def N(v, n): return str(v).rjust(n, '0')[-n:]  # numeric: right-justified, zero-filled


CREDIT = {'21', '22', '23', '24', '31', '32', '33', '34', '41', '42', '43', '44', '51', '52', '53', '54'}


def build(spec, pad=True):
    """Returns the list of 94-character records for a file description."""
    L = ['1' + '01' + A(spec['dest'].rjust(10), 10) + A(spec['origin'].rjust(10), 10) + spec['date'] + spec['time'] + spec.get('mod', 'A') + '094' + '10' + '1'
         + A(spec['dest_name'], 23) + A(spec['origin_name'], 23) + A(spec.get('ref', ''), 8)]
    seq = 0
    f_count = f_hash = f_dr = f_cr = 0
    for bn, b in enumerate(spec['batches'], 1):
        L.append('5' + b['svc'] + A(b['company'], 16) + A(b.get('disc', ''), 20) + A(b['cid'], 10) + b['sec'] + A(b['desc'], 10) + A(b.get('ddate', ''), 6)
                 + b['eff'] + '   ' + '1' + b['odfi'] + N(bn, 7))
        count = hsh = dr = cr = 0
        for e in b['entries']:
            seq += 1
            trace = b['odfi'] + N(e.get('seq', seq), 7)
            add = e.get('add', [])
            has = '1' if (add or 'ret' in e or 'noc' in e) else '0'
            if b['sec'] == 'CTX':
                rec = '6' + e['code'] + e['rt'] + A(e['acct'], 17) + N(e['amt'], 10) + A(e.get('id', ''), 15) + N(len(add), 4) + A(e['name'], 16) + '  ' + A(e.get('disc', ''), 2) + has + trace
            else:
                rec = '6' + e['code'] + e['rt'] + A(e['acct'], 17) + N(e['amt'], 10) + A(e.get('id', ''), 15) + A(e['name'], 22) + A(e.get('disc', ''), 2) + has + trace
            L.append(rec); count += 1
            hsh += int(e['rt'][:8])
            if e['code'] in CREDIT: cr += e['amt']
            else: dr += e['amt']
            for i, text in enumerate(add, 1):
                L.append('7' + '05' + A(text, 80) + N(i, 4) + trace[8:]); count += 1
            if 'ret' in e:   # return: reason, original trace, date of death, original RDFI, addenda information
                r = e['ret']; L.append('7' + '99' + r[0] + r[1] + A(r[2], 6) + r[3] + A(r[4], 44) + trace); count += 1
            if 'noc' in e:   # notification of change: change code, original trace, original RDFI, corrected data
                c = e['noc']; L.append('7' + '98' + c[0] + c[1] + A('', 6) + c[2] + A(c[3], 29) + A('', 15) + trace); count += 1
        L.append('8' + b['svc'] + N(count, 6) + N(hsh % 10 ** 10, 10) + N(dr, 12) + N(cr, 12) + A(b['cid'], 10) + A('', 19) + A('', 6) + b['odfi'] + N(bn, 7))
        f_count += count; f_hash += hsh; f_dr += dr; f_cr += cr
    blocks = -(-(len(L) + 1) // 10)
    L.append('9' + N(len(spec['batches']), 6) + N(blocks, 6) + N(f_count, 8) + N(f_hash % 10 ** 10, 10) + N(f_dr, 12) + N(f_cr, 12) + A('', 39))
    if pad:
        while len(L) % 10: L.append('9' * 94)
    assert all(len(x) == 94 for x in L), [len(x) for x in L if len(x) != 94]
    return L


ODFI = '07640125'
ORIG = {'dest': R(ODFI), 'origin': '1234567890', 'date': '261110', 'time': '0830', 'dest_name': 'FIRST EXAMPLE BANK', 'origin_name': 'ACME WIDGETS INC', 'batches': [
    {'svc': '220', 'company': 'ACME WIDGETS INC', 'cid': '1234567890', 'sec': 'PPD', 'desc': 'PAYROLL', 'ddate': 'NOV 13', 'eff': '261113', 'odfi': ODFI, 'entries': [
        {'code': '22', 'rt': R('09100001'), 'acct': '4410029384', 'amt': 245000, 'id': 'EMP-0001', 'name': 'JORDAN P RIVERA'},
        {'code': '32', 'rt': R('11300056'), 'acct': '00712230981', 'amt': 198750, 'id': 'EMP-0002', 'name': 'SAM T OKAFOR'},
        {'code': '22', 'rt': R('05300112'), 'acct': '7781234', 'amt': 312040, 'id': 'EMP-0003', 'name': 'ALEX M CHEN'},
        {'code': '23', 'rt': R('12100035'), 'acct': '55500912', 'amt': 0, 'id': 'EMP-0004', 'name': 'TAYLOR J NOWAK'},      # prenote
        {'code': '22', 'rt': R('06100070'), 'acct': '9002146655', 'amt': 221500, 'id': 'EMP-0005', 'name': 'MORGAN L PATEL'},
        {'code': '32', 'rt': R('10100019'), 'acct': '40018822', 'amt': 176325, 'id': 'EMP-0006', 'name': 'PRIYA N LINDQVIST'}]},
    {'svc': '220', 'company': 'ACME WIDGETS INC', 'cid': '1234567890', 'sec': 'CCD', 'desc': 'VENDOR PAY', 'eff': '261113', 'odfi': ODFI, 'entries': [
        {'code': '22', 'rt': R('02100008'), 'acct': '830017734', 'amt': 1250000, 'id': 'V-20418', 'name': 'NORTHWIND SUPPLY CO', 'add': ['RMR*IV*INV-10442**12500.00\\']},
        {'code': '22', 'rt': R('07100015'), 'acct': '19004452', 'amt': 487500, 'id': 'V-20077', 'name': 'LAKESIDE FREIGHT LLC', 'add': ['RMR*IV*LF-88213**4875.00\\']}]},
    {'svc': '225', 'company': 'ACME WIDGETS INC', 'cid': '1234567890', 'sec': 'WEB', 'desc': 'PURCHASE', 'eff': '261113', 'odfi': ODFI, 'entries': [
        {'code': '27', 'rt': R('04400003'), 'acct': '111222333', 'amt': 4999, 'id': 'ORD-77120', 'name': 'CASEY DUBOIS', 'disc': 'S'},
        {'code': '27', 'rt': R('08100051'), 'acct': '660041', 'amt': 12950, 'id': 'ORD-77133', 'name': 'RILEY KAPOOR', 'disc': 'S'},
        {'code': '37', 'rt': R('03100020'), 'acct': '5550100200', 'amt': 2500, 'id': 'SUB-00418', 'name': 'DEVON ALVAREZ', 'disc': 'R'}]},
]}

RDFI = '06200019'   # the bank that sends the returns
RET = {'dest': R(ODFI), 'origin': R(RDFI), 'date': '261117', 'time': '0615', 'dest_name': 'FIRST EXAMPLE BANK', 'origin_name': 'SOUTHERN EXAMPLE CU', 'batches': [
    {'svc': '200', 'company': 'ACME WIDGETS INC', 'cid': '1234567890', 'sec': 'PPD', 'desc': 'PAYROLL', 'eff': '261118', 'odfi': RDFI, 'entries': [
        {'code': '21', 'rt': R(ODFI), 'acct': '4410029384', 'amt': 245000, 'id': 'EMP-0001', 'name': 'JORDAN P RIVERA', 'ret': ['R03', ODFI + '0000001', '', '09100001', 'NO ACCOUNT/UNABLE TO LOCATE']},
        {'code': '21', 'rt': R(ODFI), 'acct': '9002146655', 'amt': 221500, 'id': 'EMP-0005', 'name': 'MORGAN L PATEL', 'ret': ['R02', ODFI + '0000005', '', '06100070', '']}]},
    {'svc': '200', 'company': 'ACME WIDGETS INC', 'cid': '1234567890', 'sec': 'WEB', 'desc': 'PURCHASE', 'eff': '261118', 'odfi': RDFI, 'entries': [
        {'code': '26', 'rt': R(ODFI), 'acct': '111222333', 'amt': 4999, 'id': 'ORD-77120', 'name': 'CASEY DUBOIS', 'disc': 'S', 'ret': ['R01', ODFI + '0000009', '', '04400003', '']},
        {'code': '26', 'rt': R(ODFI), 'acct': '660041', 'amt': 12950, 'id': 'ORD-77133', 'name': 'RILEY KAPOOR', 'disc': 'S', 'ret': ['R10', ODFI + '0000010', '', '08100051', 'CUSTOMER ADVISES NOT AUTHORIZED']},
        {'code': '36', 'rt': R(ODFI), 'acct': '5550100200', 'amt': 2500, 'id': 'SUB-00418', 'name': 'DEVON ALVAREZ', 'disc': 'R', 'ret': ['R07', ODFI + '0000011', '', '03100020', 'AUTHORIZATION REVOKED']}]},
    {'svc': '200', 'company': 'ACME WIDGETS INC', 'cid': '1234567890', 'sec': 'COR', 'desc': 'PAYROLL', 'eff': '261118', 'odfi': RDFI, 'entries': [
        {'code': '31', 'rt': R(ODFI), 'acct': '00712230981', 'amt': 0, 'id': 'EMP-0002', 'name': 'SAM T OKAFOR', 'noc': ['C01', ODFI + '0000002', '11300056', '00712230991']},
        {'code': '21', 'rt': R(ODFI), 'acct': '7781234', 'amt': 0, 'id': 'EMP-0003', 'name': 'ALEX M CHEN', 'noc': ['C02', ODFI + '0000003', '05300112', R('05300125')]},
        {'code': '21', 'rt': R(ODFI), 'acct': '55500912', 'amt': 0, 'id': 'EMP-0004', 'name': 'TAYLOR J NOWAK', 'noc': ['C05', ODFI + '0000004', '12100035', '32']}]},
]}


def write(name, lines, eol='\n', final=True):
    (OUT / name).write_bytes((eol.join(lines) + (eol if final else '')).encode('ascii'))
    print(f'{name}: {len(lines)} records')


def setf(rec, start, end, value):
    """Overwrite positions start..end (1-based, inclusive) of a record."""
    assert len(value) == end - start + 1
    return rec[:start - 1] + value + rec[end:]


OUT.mkdir(parents=True, exist_ok=True)
good = build(ORIG)
write('nacha-ppd-ccd-web-valid.ach', good)
write('nacha-valid-crlf.ach', good, '\r\n')
write('nacha-valid-no-line-breaks.ach', good, '', final=False)
write('nacha-returns-and-noc.ach', build(RET))

# ---- the same origination file with nine planted mistakes ------------------------------------------------------------
bad = build(ORIG, pad=False)
i = {k: n for n, k in enumerate(['fh', 'b1', 'e1', 'e2', 'e3', 'e4', 'e5', 'e5b', 'c1', 'b2', 'e6', 'a6', 'e7', 'a7', 'c2', 'b3', 'e8', 'e9', 'e10', 'c3', 'fc'])}
bad[i['e3']] = setf(bad[i['e3']], 12, 12, str((int(bad[i['e3']][11]) + 1) % 10))         # 1 wrong ABA check digit
bad[i['c1']] = setf(bad[i['c1']], 33, 44, N(int(bad[i['c1']][32:44]) + 10000, 12))       # 2 batch 1 credit total $100.00 too high
bad[i['e1']], bad[i['e2']] = bad[i['e2']], bad[i['e1']]                                  # 3 trace numbers not ascending
bad[i['b1']] = setf(bad[i['b1']], 54, 63, A('SALARY', 10))                               # 4 PPD credits not described as PAYROLL
bad[i['c2']] = setf(bad[i['c2']], 11, 20, N(int(bad[i['c2']][10:20]) + 1, 10))           # 5 batch 2 entry hash off by one
bad[i['a7']] = setf(bad[i['a7']], 84, 87, '0002')                                        # 6 addenda sequence number 2 on the only addenda
bad[i['b3']] = setf(bad[i['b3']], 54, 63, A('ONLINE ORD', 10))                           # 7 WEB debits not described as PURCHASE
bad[i['fc']] = setf(bad[i['fc']], 14, 21, N(int(bad[i['fc']][13:21]) - 1, 8))            # 8 file entry/addenda count one short
write('nacha-with-errors.ach', bad)                                                     # 9 the 9-filled padding records are missing (21 records instead of 30)
