# WatchLog Insights - Data Sources Documentation

## Overview

이 문서는 WatchLog Insights 애플리케이션에서 사용하는 데이터 소스와 mock 데이터에 대해 설명합니다.

## YouTube API 제약사항

YouTube Data API v3는 개인정보 보호를 위해 **직접적인 시청 기록(watch history)에 접근할 수 없습니다**. 이는 2016년 9월부터 시행된 정책으로, 다음과 같은 데이터에 접근이 제한됩니다:

- 개인 시청 기록 (Watch History)
- 나중에 볼 동영상 목록 (Watch Later)
- 실제 시청 시간
- 구체적인 시청 일시

## 실제 YouTube API에서 가져오는 데이터

### 1. 채널 정보 (Channel Information)
- **API 엔드포인트**: `channels().list()`
- **데이터 항목**:
  - 채널 이름
  - 채널 ID
  - 채널 통계 (구독자 수, 총 조회수 등)
  - 채널 설명

### 2. 플레이리스트 (Playlists)
- **API 엔드포인트**: `playlists().list()`
- **데이터 항목**:
  - 사용자가 생성한 플레이리스트 목록
  - 플레이리스트 제목 및 설명
  - 플레이리스트 내 비디오 목록

### 3. 구독 정보 (Subscriptions)
- **API 엔드포인트**: `subscriptions().list()`
- **데이터 항목**:
  - 구독한 채널 목록
  - 채널명

### 4. 비디오 카테고리 (Video Categories)
- **API 엔드포인트**: `videoCategories().list()`
- **데이터 항목**:
  - YouTube 표준 카테고리 목록
  - 카테고리 ID 및 이름

### 5. 비디오 메타데이터 (Video Metadata)
- **API 엔드포인트**: `videos().list()`
- **데이터 항목**:
  - 비디오 제목
  - 비디오 설명
  - 카테고리 ID
  - 업로드 채널명

## Mock 데이터 (Simulated Data)

다음 데이터는 YouTube API에서 제공되지 않으므로 시뮬레이션됩니다:

### 1. 시청 시간 (Watch Time)
- **데이터**: `watch_time_minutes`
- **생성 방법**: 5분~120분 사이의 랜덤 값
- **목적**: 대시보드 차트와 통계 표시를 위해

### 2. 시청 일시 (Watch Timestamp)
- **데이터**: `watched_at`
- **생성 방법**: 지정된 기간 내 랜덤 날짜/시간
- **목적**: 시간별/요일별 패턴 분석을 위해

### 3. 시청 기록 구조
```python
VideoData(
    video_id="video_123",           # Mock ID
    title="Real Video Title",       # Real from API
    channel_name="Real Channel",    # Real from API/subscriptions
    category_id=27,                 # Real from API
    category_name="Education",      # Real from API
    watch_time_minutes=45,          # MOCK - simulated
    watched_at="2024-01-15T14:30:00"  # MOCK - simulated
)
```

## 데이터 통합 로직

### Enhanced Mock Data Generation
애플리케이션은 실제 API 데이터와 mock 데이터를 조합하여 다음과 같이 작동합니다:

1. **실제 데이터 수집**:
   ```python
   channel_info = await get_user_channel_info(youtube_service)
   playlists = await get_user_playlists(youtube_service)
   subscriptions = await get_user_subscriptions(youtube_service)
   categories = await get_video_categories(youtube_service)
   ```

2. **데이터 조합**:
   - 구독 채널에서 실제 채널명 추출
   - 실제 카테고리 정보 사용
   - 플레이리스트에서 실제 비디오 제목 추출
   - 시청 시간과 일시는 mock 데이터로 생성

3. **Fallback 메커니즘**:
   - API 호출 실패 시 완전한 mock 데이터로 전환
   - 사용자에게 데이터 소스 상태 알림

## API 함수별 세부사항

### `generate_enhanced_videos()`
실제 YouTube 데이터와 mock 데이터를 조합하여 비디오 목록 생성

**입력**: YouTube API 서비스 객체, 분석 기간(일)
**출력**: VideoData 객체 리스트
**처리 과정**:
1. 실제 채널, 플레이리스트, 구독 정보 수집
2. 실제 카테고리 정보로 매핑 테이블 생성
3. 플레이리스트에서 실제 비디오 정보 추출
4. Mock 시청 시간과 일시 생성
5. 조합된 데이터로 VideoData 객체 생성

### `get_user_channel_info()`
사용자의 채널 정보 조회

### `get_user_subscriptions()`
사용자가 구독한 채널 목록 조회

### `get_video_categories()`
YouTube 표준 카테고리 목록 조회

## 사용자 알림

애플리케이션은 다음과 같은 방식으로 사용자에게 데이터 소스를 알립니다:

### 1. 데이터 소스 정보 패널
```
📘 About Your Data
Due to YouTube API privacy restrictions, actual watch history is not accessible.
This dashboard shows:
• Real data: Your channel info, subscriptions, playlists, and video categories
• Simulated data: Watch times and viewing timestamps (for demo purposes)
```

### 2. 동기화 결과 알림
- 성공: 연결된 채널명과 실제 데이터 동기화 완료
- 부분 성공: API 연결되었으나 일부 데이터만 사용 가능
- 실패: Mock 데이터로 전환됨을 알림

## 향후 개선 방안

### 1. 대안 데이터 소스
- Google Takeout을 통한 시청 기록 가져오기
- 브라우저 확장 프로그램을 통한 클라이언트 사이드 추적
- 사용자 수동 입력 시스템

### 2. 실제 데이터 확장
- 좋아요한 비디오 목록 활용
- 댓글 작성한 비디오 추적
- 업로드한 비디오 분석

### 3. AI 기반 분석
- 구독 채널과 플레이리스트 기반 시청 패턴 예측
- 카테고리 선호도 분석
- 개인화된 추천 시스템

## 개발자 참고사항

### Mock 데이터 수정
Mock 데이터 생성 로직은 `backend/main.py`의 다음 함수들에서 관리됩니다:
- `generate_enhanced_videos()`: 통합 데이터 생성
- `generate_mock_videos()`: Fallback mock 데이터 생성

### 새로운 실제 데이터 추가
새로운 YouTube API 데이터를 추가하려면:
1. `backend/main.py`에 API 헬퍼 함수 추가
2. `generate_enhanced_videos()`에서 새 데이터 통합
3. 프론트엔드에서 새 데이터 필드 처리

### 테스트
개발 중에는 `MOCK_DATA_ONLY=true` 환경 변수를 설정하여 API 호출 없이 mock 데이터만 사용할 수 있습니다.

---

**마지막 업데이트**: 2024년 12월
**문서 버전**: v1.0