"""우리FIS 제출용 PDF. 실행: python tools/build_woorifis_portfolio.py

필수: reportlab. 기본 글꼴은 Windows 맑은 고딕이며 공식 브랜드 서체가 아니다.
다른 OS는 --font, --bold-font에 한글 TrueType 글꼴 경로를 지정한다.
"""

import argparse
import re
from html import escape
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output/pdf/김소령_우리FIS_IT자원관리운영_포트폴리오.pdf'
W, H = landscape(A4)
M = 42
CW = W - M * 2
INK, BODY, MUTED = '#000000', '#333333', '#666666'
BLUE, LINE, PALE = '#0067AC', '#CCCCCC', '#F5F5F5'
PAGES = 12


def build(output, font, bold_font):
    pdfmetrics.registerFont(TTFont('KR', str(font)))
    pdfmetrics.registerFont(TTFont('KR-Bold', str(bold_font)))
    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=(W, H), pageCompression=1)
    c.setTitle('김소령 | 우리FIS IT자원관리·운영 포트폴리오')
    c.setAuthor('김소령')
    c.setSubject('IT 자산·유지보수·예산·내부통제·재해대응 경험')
    c.setCreator('김소령 포트폴리오')
    page = 0
    rendered_text = []

    def rule(x, y, width, color=LINE, weight=0.6):
        c.setStrokeColor(HexColor(color))
        c.setLineWidth(weight)
        c.line(x, H-y, x+width, H-y)

    def rect(x, y, width, height, fill=None):
        c.setStrokeColor(HexColor(LINE))
        c.setLineWidth(0.6)
        if fill:
            c.setFillColor(HexColor(fill))
        c.rect(x, H-y-height, width, height, stroke=1, fill=bool(fill))

    def text(value, x, y, width, size=11, color=BODY, bold=False, max_h=100):
        rendered_text.append(value)
        assert 0 <= x < W and x+width <= W+0.1
        style = ParagraphStyle('text', fontName='KR-Bold' if bold else 'KR',
                               fontSize=size, leading=size*1.48, textColor=HexColor(color),
                               alignment=TA_LEFT, wordWrap='CJK', splitLongWords=True)
        para = Paragraph(escape(value).replace('\n', '<br/>'), style)
        _, height = para.wrap(width, max_h)
        assert height <= max_h+0.1, f'Page {page}: text too tall ({height:.1f}>{max_h}): {value[:45]}'
        assert y+height <= H-16, f'Page {page}: text off page: {value[:45]}'
        para.drawOn(c, x, H-y-height)
        return height

    def start(section, title, subtitle):
        nonlocal page
        page += 1
        c.bookmarkPage(f'p{page}')
        c.addOutlineEntry(title, f'p{page}')
        text(section, M, 25, 470, 9, BLUE, True, 18)
        text('김소령  /  우리FIS 지원 포트폴리오', W-280, 25, 238, 8.5, MUTED, max_h=18)
        rule(M, 49, CW, BLUE, 1.1)
        text(title, M, 68, CW, 26, INK, True, 42)
        text(subtitle, M, 113, CW, 11, BODY, max_h=36)

    def end(source):
        rule(M, 515, CW)
        text(source, M, 523, CW, 8, MUTED, max_h=26)
        text('IT RESOURCE MANAGEMENT & OPERATIONS', M, 559, 500, 8, MUTED, max_h=15)
        text(f'{page:02d} / {PAGES:02d}', W-94, 557, 55, 9, BLUE, True, 18)
        c.showPage()

    def block(label, body, x, y, width, max_h=90):
        text(label, x, y, width, 12, INK, True, 23)
        return text(body, x, y+27, width, 11, BODY, max_h=max_h)

    def table(headers, rows, x, y, widths, row_h=49, size=10):
        total = sum(widths)
        rect(x, y, total, 32, PALE)
        pos = x
        for header, width in zip(headers, widths):
            text(header, pos+10, y+7, width-20, 10, INK, True, 20)
            pos += width
        y += 32
        for row in rows:
            pos = x
            for value, width in zip(row, widths):
                text(value, pos+10, y+10, width-20, size, BODY, max_h=row_h-17)
                pos += width
            rule(x, y+row_h, total)
            y += row_h
        return y

    def steps(items, x, y, width, height=78):
        gap = 16
        cell = (width-gap*(len(items)-1))/len(items)
        for i, (label, body) in enumerate(items):
            px = x+i*(cell+gap)
            rect(px, y, cell, height)
            text(f'{i+1:02d}  {label}', px+11, y+11, cell-22, 10.5, INK, True, 22)
            text(body, px+11, y+36, cell-22, 9.5, BODY, max_h=height-43)
            if i < len(items)-1:
                rule(px+cell+3, y+height/2, gap-6, MUTED)

    # 01 / 표지: 공식 로고·그라데이션을 복제하지 않는 지원자 문서.
    page += 1
    c.bookmarkPage('p1')
    c.addOutlineEntry('김소령 포트폴리오', 'p1')
    text('WOORIFIS  /  IT RESOURCE MANAGEMENT & OPERATIONS', M, 37, CW, 10, BLUE, True, 20)
    rule(M, 71, CW, BLUE, 1.5)
    text('IT 자원·비용·통제를\n하나의 운영 흐름으로', M, 115, 525, 33, INK, True, 112)
    text('김소령', M, 268, 450, 25, INK, True, 42)
    text('우리FIS IT자원관리/운영 지원', M, 313, 490, 13, BODY, max_h=23)
    text('서비스 운영의 맥락을 이해하고, 유지보수·예산·보안과\n변경·복구 절차를 함께 관리해 온 경험을 담았습니다.',
         M, 350, 493, 12, BODY, max_h=47)
    text('SELECTED CASES', 611, 117, 190, 9, BLUE, True, 20)
    for idx, title in enumerate(['자산·유지보수·예산', 'SSL 배포·현황관리', 'ISMS·서버 보안', '재해대응 도상훈련']):
        y = 151+idx*53
        text(f'0{idx+1}', 611, y, 30, 10, BLUE, True, 20)
        text(title, 645, y, 155, 10.5, BODY, max_h=34)
        rule(611, y+35, 189)
    for x, value, label in [(M, '월별', '부서 예산 현황 직접 보고'), (M+259, '25대', 'SSL 운영 적용 / 2026.09'), (M+518, '16대', 'Linux 중앙 로그 수집')]:
        rule(x, 427, 238, INK, 1)
        text(value, x, 438, 238, 27, BLUE, True, 44)
        text(label, x, 485, 238, 9.5, BODY, max_h=20)
    end('2026.09 | 개인 지원 포트폴리오. 내부 금액·주소·계정·연락처를 제외하고 수행 범위와 검증 가능한 사실 중심으로 구성했습니다.')

    # 02 / 공고와 경험의 연결.
    start('OVERVIEW', '기술 운영과 관리 업무를 함께 연결합니다',
          '유지보수·비용·현황·통제를 직접 다룬 경험을 중심에 두고, 재해복구는 실제 참여 범위를 구분했습니다.')
    table(['공고의 주요 업무', '연결되는 수행 경험', '관련 페이지'], [
        ['인프라 유지보수', '운영 자산, 솔루션·라이선스 갱신, 협력사 일정 조율', '03-04'],
        ['관리회계·예산', '월별 예산·실적 보고, 관리 파일 유지, 전용·이월 신청', '03-04'],
        ['인프라 운영 현황', 'SSL 현황·검증 자동화, Linux 16대 중앙 로그 수집', '05-06 / 09'],
        ['부서 내부통제', '서버 위험조치, ISMS 증적, 네트워크 등록·회수 기록', '07 / 09'],
        ['재해복구 환경 관리', '복구 절차·전파체계 점검 및 도상훈련 참여', '08'],
    ], M, 165, [155, 489, CW-644], row_h=48, size=10.5)
    text('경험의 경계', M, 460, 95, 10.5, INK, True, 20)
    text('부서 예산관리 실무와 도상훈련 경험입니다. 본부 예산 집행·승인, 실제 DR센터 전환,\n금융권 인프라 및 전용 CMDB/ITSM 운영 경험으로 확대해 표현하지 않습니다.',
         M+112, 458, CW-112, 10, BODY, max_h=36)
    end('기준 공고: 우리FIS IT자원관리/운영 경력 채용. 관련 사례는 개인 업무기록과 참여 산출물에 기반합니다.')

    # 03 / 자원·비용.
    start('CASE 01  /  ASSETS, MAINTENANCE & BUDGET', '운영 대상과 유지보수·예산을 함께 관리',
          '상시 업무 | 자산 현황, 계약·라이선스 갱신, 부서 예산관리 및 월별 비용 마감 실무')
    block('문제와 판단', 'IDC·CDN·검색·메시징·유지보수·라이선스는 갱신 주기와 비용 처리 시점이 다릅니다.\n\n금액만 확인하지 않고 서비스의 운영 필요성, 계약 기간, 갱신 시점과 예산 현황을 함께 살폈습니다.',
          M, 169, 250, 160)
    text('직접 담당한 업무', 328, 169, 470, 12, INK, True, 22)
    table(['영역', '담당 범위'], [
        ['자산·상태', 'IDC 실물 서버 목록 반영, 운영 상태 확인·공유'],
        ['유지보수', '솔루션 재계약, 라이선스 갱신, 협력사 일정 조율'],
        ['예산 보고', '관리 파일 유지, 월별 예산·실적 현황 직접 보고'],
        ['예산 조정', '부족 예산 및 일정 변경에 따른 전용·이월 신청'],
        ['비용 마감', '실비·세금계산서·비용보고 자료 정리'],
    ], 328, 201, [102, CW-286-102], row_h=45, size=10.2)
    rule(M, 405, 250, INK, 1)
    text('남긴 산출물', M, 421, 250, 12, INK, True, 22)
    text('월별 비용예산 관리 파일\n예산 보고·전용·이월 신청\n유지보수·갱신 및 비용 마감 기록', M, 452, 250, 10.5, BODY, max_h=50)
    end('근거: 월별 비용예산 자료, 2026년 업무주간보고, 업무분장 기록. 담당 범위는 부서 예산관리 실무이며 집행·승인 권한을 의미하지 않습니다.')

    # 04 / 숫자와 내부 원본을 노출하지 않는 증빙 편집.
    start('CASE 01  /  EVIDENCE & DECISIONS', '기술 대상·기간·예산을 연결한 관리 기록',
          '업무기록 기반 재구성 | 실제 계약서·회계 화면이 아닌, 수행 업무와 확인 기준의 비식별 요약입니다.')
    steps([('대상 확인', '운영 서비스·계약·갱신'), ('현황 보고', '월별 예산·실적 정리'), ('변경 확인', '예산 부족·시점 변경'), ('신청·관리', '전용·이월 및 자료 관리')], M, 164, CW, 76)
    table(['확인된 업무 사례', '관리 관점', '확인할 수 있는 산출물'], [
        ['CDN·검색 솔루션 재계약', '운영 지속 필요성과 갱신 일정 연결', '재계약·과금 이력, 업무보고'],
        ['메시징 솔루션 예산 이월', '예산과 업무 진행 시점의 차이 확인', '이월 신청 및 비용예산 자료'],
        ['유지보수·라이선스 갱신', '기술 대상·지원 기간·협력사 일정 확인', '발주·갱신 및 처리 기록'],
        ['월별 예산·비용 마감', '예산·실적과 당월 처리 자료 정리', '비용예산 관리 파일, 월별 보고'],
    ], M, 264, [210, 280, CW-490], row_h=48, size=10.2)
    text('핵심 역량: 기술 대상과 비용의 연결을 이해하고, 갱신·예산·보고 일정을 유관 부서 및 협력사와 조율합니다.',
         M, 490, CW, 9, MUTED, max_h=18)
    end('근거: 비용예산 관리 파일(2025-2026), 2026년 업무주간보고의 갱신·예산 이월·마감 기록. 거래 조건, 금액과 개인정보는 제외했습니다.')

    # 05 / SSL.
    start('CASE 02  /  SSL AUTOMATION  /  2026.06-09', '인증서 교체를 검증 가능한 변경으로',
          'Ansible · Python · Shell · OpenSSL | 탐지·배포·실제 응답 확인·복구를 공통 운영 절차로 구성')
    text('25대', M, 168, 227, 42, BLUE, True, 67)
    text('2026년 9월 운영 대상 적용', M, 237, 242, 11, BODY, max_h=22)
    rule(M, 279, 242, INK, 1)
    block('문제', 'Apache·Tomcat·Resin·NetFUNNEL의 인증서 경로와 재기동 방식이 달랐습니다.\n\n파일 교체 성공만으로 실제 서비스에 새 인증서가 반영됐다고 판단할 수 없었습니다.',
          M, 296, 242, 156)
    text('핵심 설계 결정', 325, 170, 470, 13, INK, True, 24)
    for y, label, body in [
        (210, '활성 설정에서 실제 경로 탐지', '실행 프로세스·활성 설정으로 인증서 적용 대상을 확인했습니다.'),
        (280, '파일 배치와 서비스 활성화 분리', '사전 검증 후 순차 배포하고 승인 시간대에 재기동했습니다.'),
        (350, '실제 서비스 응답으로 완료 판단', 'SHA-256 지문과 live 443 응답을 확인했습니다.'),
        (420, '실패 시 원복 가능한 작업', '사전 백업과 자동 롤백을 실행 가이드에 포함했습니다.'),
    ]:
        rule(325, y-9, CW-283)
        block(label, body, 325, y, CW-283, 39)
    end('근거: SSL 자동 배포 실행 가이드·롤백 가이드·대시보드 명세, 2026년 업무보고. 25대는 9월 운영 적용 기준이며 탐지·계획 대상 수와 구분합니다.')

    # 06 / 검증·복구를 포함한 변화 흐름.
    start('CASE 02  /  VALIDATION & RECOVERY', '배포 성공보다 서비스 반영을 확인합니다',
          '실제 운영 절차를 재구성한 흐름도 | 단계를 통과한 조건과 실패 시 행동을 함께 관리')
    steps([('dry-run', '설정·입력 사전 검증'), ('canary', '1대 우선 적용·확인'), ('순차 배포', '백업·파일 배치'), ('승인·활성화', '재기동·live 검증')], M, 162, CW, 76)
    table(['통제 지점', '판단 기준', '조치·기록'], [
        ['경로·재기동', '실행 중인 서비스의 활성 설정·명령 확인', '잘못된 실행 명령 발견 시 수정 후 재배포'],
        ['실제 응답', '배치 파일과 live 443의 지문·체인 검증', '실패 시 이전 인증서로 자동 롤백'],
        ['현황 관리', '만료일·적용 경로·수집 지연 확인', 'HTML/JSON 대시보드와 실행 기록'],
    ], M, 263, [136, 330, CW-466], row_h=49, size=10.1)
    rect(M, 460, CW, 40, PALE)
    text('운영에서 확인한 예외: Resin 실행 명령과 인증서 체인 조립 오류를 자동 롤백 후 수정·재배포해 검증했습니다.',
         M+12, 470, CW-24, 10, BODY, max_h=24)
    end('근거: SSL 실행·복구 가이드와 운영 검증 기록. 도식은 설명용 재구성이며 내부 서버명·도메인·인증서 원문은 포함하지 않습니다.')

    # 07 / ISMS.
    start('CASE 03  /  SECURITY & INTERNAL CONTROL  /  2024-2026', '보안 진단을 서비스 영향과 조치 증적으로 연결',
          '직접 수행 범위 | Linux·Windows·WEB/WAS 보안 조치, 재점검, 운영 증적 및 잔여 위험 관리')
    table(['대상', '직접 수행한 조치', '작업 전후 확인'], [
        ['Linux', '홈·로그 파일 권한, 비밀번호 정책', '계정·소유권 확인, 설정 백업·재진단'],
        ['WEB/WAS', 'Apache·Tomcat 노출·업로드 관련 설정', '서비스 구조·재기동 영향, 문법·상태 검증'],
        ['Windows·표준 이미지', '누적 보안 업데이트, Golden Image 점검', '작업 순서 확인, 표준 기준과 결과 기록'],
    ], M, 164, [150, 302, CW-452], row_h=53, size=10.1)
    text('2026년 7월 보고 기준', M, 384, 245, 11, INK, True, 21)
    for y, label, ratio in [(423, 'Linux 잔여 위험조치', 1.0), (458, 'Windows 서버 조치', 0.9)]:
        text(label, M, y, 175, 10, BODY, max_h=20)
        rect(M+181, y+4, 165, 9, PALE)
        c.setFillColor(HexColor(BLUE))
        c.rect(M+181, H-y-13, 165*ratio, 9, stroke=0, fill=1)
        text(f'{ratio:.0%}', M+357, y-2, 66, 11, BLUE, True, 23)
    block('확인된 결과', '2025년 ISMS 심사·결함 조치를 기한 내 수행해 인증 유지에 기여했습니다.\n\n좌측 수치는 해당 시점의 조치 진행률이며 전사 보안 수준을 의미하지 않습니다.',
          502, 385, CW-460, 98)
    end('근거: 2025 성과평가, 2026 KPI·7월 업무보고, 서버 위험조치 기록. 공용 통제 문서 전체의 설계·감사 책임을 개인 수행으로 주장하지 않습니다.')

    # 08 / DR: 실전 전환과 명확하게 분리.
    start('CASE 04  /  DISASTER RESPONSE  /  2025.10', '복구 절차를 비상시에 실행할 수 있는지 점검',
          'IT재해대응 도상훈련 참여 | DB·WEB/WAS 중단을 가정한 절차·역할·의사결정 확인')
    steps([('인지·전파', '연락망·보고체계 확인'), ('복구 기준', 'RTO·RPO·우선순위'), ('대응 토의', '역할·복구 전략 확인'), ('개선 도출', '연락체계·절차 숙련')], M, 163, CW, 76)
    table(['결과보고서에서 확인된 사항', '개선 방향', '현재 자료의 범위'], [
        ['담당자 연락처 현행화 미비', '외주 인력 변경 시 연락체계 갱신', '훈련 결과에 기록된 개선 필요사항'],
        ['데이터 복구절차 숙련도 개선 필요', '복구절차 숙지·데이터 복구훈련', '후속 훈련 계획이며 완료 성과와 구분'],
        ['복구 목표시간·시점 인지: 양호', '복구 우선순위·판단 기준의 반복 점검', '목표 인지 점검이며 실제 복구시간 측정 아님'],
    ], M, 263, [268, 235, CW-503], row_h=54, size=10)
    rect(M, 471, CW, 32, PALE)
    text('참여 범위: 절차 점검·도상훈련. 실제 DR센터 전환 및 AWS DR 환경 구축 경험으로 표현하지 않습니다.',
         M+10, 478, CW-20, 9.5, BODY, max_h=19)
    end('근거: 2025년 2차 IT재해대응훈련 계획서·결과보고서(공용). 문서 내 예시 시나리오와 실제 훈련 결과를 구분해 재구성했습니다.')

    # 09 / 관련 기술 깊이.
    start('RELATED EXPERIENCE  /  OPERATIONS TOOLS', '현황을 모으고, 반복 증적의 불일치를 줄입니다',
          '운영 자동화와 로그 수집 환경을 직접 구성한 보완 경험')
    col = (CW-30)/2
    for x in [M, M+col+30]:
        rule(x, 166, col, INK, 1.1)
    block('ELK 기반 중앙 로그 수집·분석', '2024 | Linux 16대\n\n상용 솔루션 구매 제약을 고려해 Filebeat - Logstash - Elasticsearch - Kibana 수집 환경을 구축했습니다.',
          M, 182, col, 99)
    block('입·퇴사자 네트워크·보안 증적 자동화', '2026 | 본사·외부 인원 4개 처리 유형\n\nIP/MAC 관리대장, ISMS 입·퇴사 증적, 월별 무선랜 현황을 한 번의 입력으로 연계했습니다.',
          M+col+30, 182, col, 99)
    block('운영 기준', 'Java 다중행 오류를 한 이벤트로 처리\n일별 압축 백업 및 180일 보관\nHTTPS·계정 분리 적용\n권한·버전 잔재·방화벽·인증 오류 분석',
          M, 337, col, 94)
    block('데이터 정합성 기준', '수정 전 검증·원본 백업\n기존 IP 재사용 시 명시적 확인\n앞 단계 실패 시 후속 문서 수정 차단\n성공·건너뜀·실패 결과 요약',
          M+col+30, 337, col, 94)
    text('직무 연결: 운영 현황 파악과 장애 원인 추적', M, 479, col, 9.5, BLUE, True, 20)
    text('직무 연결: 접근 등록·회수와 증적의 일관성', M+col+30, 479, col, 9.5, BLUE, True, 20)
    end('근거: ELK 구축·이관·오류 기록, 2024 성과평가, 입·퇴사 자동화 코드·테스트와 업무기록. 전용 CMDB/ITSM·AD 프로비저닝 경험과는 구분합니다.')

    # 10 / 본인 테스트 결과.
    start('RELATED EXPERIENCE  /  SERVICE QUALITY', '서비스의 변경을 사용자 흐름과 검수로 확인',
          '온라인 멤버십 시스템(ABC-CAMP) | 퍼블리싱 검수, 단위·통합 테스트, 오픈 안정화 참여')
    text('42건', M, 165, 243, 39, BLUE, True, 65)
    text('담당 CMS 2차 통합 테스트', M, 233, 246, 11, INK, True, 22)
    text('PASS 41건 / FAIL 1건', M, 269, 246, 16, INK, True, 29)
    block('나의 역할', '사용자 화면과 운영 절차를 검수하고, 테스트 결과·테스터·일자를 남겼습니다. 실패 항목도 구분해 재확인이 가능한 기록으로 관리했습니다.',
          M, 335, 255, 113)
    table(['담당 테스트 영역', '수행 건수'], [
        ['로그인', '6건'], ['내 결재함', '10건'], ['고객 그룹 관리', '20건'], ['기획 캠페인', '6건'],
    ], 338, 168, [324, CW-296-324], row_h=45, size=10.8)
    block('운영 직무에 연결되는 관점', '퍼블리싱과 온라인 서비스 운영을 통해 사용자 화면·정적 리소스·배포 일정·인프라 변경의 접점을 이해합니다.\n요구사항을 검증 기준으로 바꾸고, 개발·운영 담당자와 변경 영향을 확인하는 데 활용할 수 있습니다.',
          338, 402, CW-296, 74)
    end('근거: 본인 CMS 2차 통합테스트 결과(42건), 2025 성과평가. 요구사항명세·오픈 체크리스트는 공용 산출물이며 전체 기획·개발 책임으로 표현하지 않습니다.')

    # 11 / 미래 기여: 수행 사실과 분리.
    start('CONTRIBUTION', '현황을 정확히 파악하고, 실행 기준을 남기겠습니다',
          '우리FIS에서의 기여 방향 | 현재의 운영·관리 경험을 금융 IT 환경의 기준에 맞춰 확장하겠습니다.')
    gap = 24
    col = (CW-gap*2)/3
    for i, (label, title, body, deliverable) in enumerate([
        ('01', '유지보수·비용의 연결', '자원과 계약 기간, 예산·실적, 협력사 일정을 함께 파악하겠습니다.\n\n월별 보고·전용·이월 신청 경험을 바탕으로 관리 업무의 연속성을 지원하겠습니다.', '현황과 일정의 일관된 관리'),
        ('02', '변경·통제의 실행력', '영향 확인, 승인, 검증과 복구 기준을 변경 업무에 연결하겠습니다.\n\nSSL 자동화·보안 조치 경험으로 운영자가 다시 확인할 수 있는 절차와 증적을 남기겠습니다.', '검증·복구 가능한 변경 기록'),
        ('03', '재해복구 역량의 확장', '도상훈련에서 확인한 연락체계·복구 우선순위·절차 숙련의 중요성을 이어가겠습니다.\n\n금융권 DR 환경과 실제 전환·복구 검증 절차는 새롭게 익힐 영역으로 명확히 두겠습니다.', '절차 이해에서 실제 검증으로'),
    ]):
        x = M+i*(col+gap)
        rule(x, 170, col, INK, 1)
        text(label, x, 187, col, 26, BLUE, True, 42)
        text(title, x, 247, col, 15, INK, True, 28)
        text(body, x, 293, col, 11, BODY, max_h=163)
        text(deliverable, x, 480, col, 9.5, BLUE, True, 20)
    end('기여 방향: 기존 운영·예산·통제 경험을 활용하며, 금융권의 실제 DR 전환·복구 검증 절차는 입사 후 습득할 영역으로 구분합니다.')

    # 12 / 근거 탐색을 돕는 최소 자료 목록.
    start('EVIDENCE INDEX', '수행 사실과 참여 범위를 확인할 수 있는 자료',
          '개인 기록·직접 작성 산출물과 프로젝트 공용 문서를 구분했습니다. 내부 원본은 외부 제출본에 첨부하지 않았습니다.')
    table(['사례·페이지', '근거 자료', '이 자료로 설명하는 범위'], [
        ['자산·예산 / 03-04', '월별 비용예산 자료(2025-2026),\n업무주간보고·업무분장 기록', '예산 보고·관리 실무, 전용·이월,\n유지보수·갱신·비용 마감'],
        ['SSL / 05-06', 'SSL 실행 가이드·롤백 가이드·대시보드 명세,\n2026년 운영 적용 기록', '탐지·배포·live 검증·복구,\n9월 25대 운영 적용'],
        ['ISMS / 07', '2025 성과평가, 2026 KPI·7월 업무보고,\n서버 위험조치 기록', '개인 서버 조치·재점검,\n인증 유지 기여 및 당시 조치 진행률'],
        ['재해대응 / 08', '2025년 2차 IT재해대응훈련 계획·결과보고서\n(조직 공용 산출물)', '도상훈련 참여와 절차 점검,\n결과보고서에 기록된 개선사항'],
        ['운영 도구 / 09', 'ELK 구축·이관·오류 기록,\n입·퇴사 자동화 코드·테스트', '로그 수집·문제 분석,\n네트워크·ISMS 증적 자동화'],
        ['ABC-CAMP / 10', '개인 CMS 2차 통합테스트 결과,\n2025 성과평가', '본인 테스트 42건과 결과,\n퍼블리싱 검수·오픈 안정화 참여'],
    ], M, 160, [137, 345, CW-482], row_h=47, size=9.3)
    text('기준 공고: 우리FIS IT자원관리/운영 경력 채용', M, 485, CW, 9, BLUE, True, 18)
    c.linkURL('https://careers.woorifis.com/job_posting/rxSudutW', (M, H-502, 450, H-482), relative=0)
    end('표·도식은 설명을 위한 비식별 재구성이며 원본 화면 캡처가 아닙니다. 이 문서는 지원자가 작성한 개인 포트폴리오로 회사 공식 자료가 아닙니다.')

    # 고정 제출본의 페이지 수, 금지 표현, 외부 공개 범위를 확인한다.
    assert page == PAGES
    all_text = '\n'.join(rendered_text)
    assert not re.search(r'차세대|28대', all_text)
    assert not re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', all_text)
    assert 'PASS 41건 / FAIL 1건' in all_text
    assert '실제 DR센터 전환 및 AWS DR 환경 구축 경험으로 표현하지 않습니다.' in all_text
    c.save()
    print(f'Created {page} landscape pages: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/malgun.ttf'))
    parser.add_argument('--bold-font', type=Path, default=Path('C:/Windows/Fonts/malgunbd.ttf'))
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    for file in (args.font, args.bold_font):
        if not file.is_file():
            parser.error(f'글꼴 파일을 찾을 수 없습니다: {file}')
    build(args.output, args.font, args.bold_font)
