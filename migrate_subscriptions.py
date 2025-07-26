import argparse
from dataclasses import dataclass
from typing import List
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

@dataclass
class Subscription:
    id: str
    title: str

# OAuth 2.0 스코프 정의
SCOPES_READ = ['https://www.googleapis.com/auth/youtube.readonly']
SCOPES_WRITE = ['https://www.googleapis.com/auth/youtube']

def get_credentials(account_name: str, scopes: List[str], client_secrets_file: str):
    """지정된 계정에 대한 Google API 인증 정보를 항상 새로 가져옵니다."""
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server(port=0)
    return credentials

def get_all_subscriptions(youtube) -> List[Subscription]:
    """YouTube 계정의 모든 구독 채널 정보를 가져와 Subscription 객체 리스트로 반환합니다."""
    subscriptions: List[Subscription] = []
    next_page_token = None

    while True:
        request = youtube.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            # 딕셔너리 대신 Subscription 객체를 생성하여 추가
            subscriptions.append(Subscription(
                id=item['snippet']['resourceId']['channelId'],
                title=item['snippet']['title']
            ))

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
            
    return subscriptions

def subscribe_to_channels(youtube, channel_ids: List[str]):
    """주어진 채널 ID 목록을 구독합니다."""
    total = len(channel_ids)
    for i, channel_id in enumerate(channel_ids):
        try:
            youtube.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "resourceId": {
                            "kind": "youtube#channel",
                            "channelId": channel_id
                        }
                    }
                }
            ).execute()
            print(f"({i+1}/{total}) Subscribed to channel: {channel_id}")
        except Exception as e:
            print(f"({i+1}/{total}) Could not subscribe to channel {channel_id}: {e}")

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="YouTube 구독 목록을 한 계정에서 다른 계정으로 이전합니다.")
    parser.add_argument('client_secrets_file', help='Google Cloud OAuth 2.0 클라이언트 시크릿 JSON 파일의 경로')
    args = parser.parse_args()

    # 1. 소스 계정 인증 및 구독 목록 가져오기
    print("--- 1. 소스 YouTube 계정으로 로그인해주세요. ---")
    source_credentials = get_credentials('source_account', SCOPES_READ, args.client_secrets_file)
    source_youtube = build('youtube', 'v3', credentials=source_credentials)
    
    print("\n소스 계정에서 구독 목록을 가져오는 중...")
    source_subscriptions_data = get_all_subscriptions(source_youtube)
    
    if not source_subscriptions_data:
        print("구독 중인 채널이 없습니다. 프로그램을 종료합니다.")
        return

    print(f"\n--- 총 {len(source_subscriptions_data)}개의 구독 채널을 찾았습니다. ---")
    for sub in source_subscriptions_data:
        # 객체의 속성에 접근 (sub['title'] -> sub.title)
        print(f"- {sub.title}")
    print("------------------------------------")

    # 2. 사용자에게 계속할지 확인
    try:
        confirmation = input("\n위 목록을 타겟 계정으로 이전하시겠습니까? (y/n): ")
    except KeyboardInterrupt:
        print("\n\n작업이 취소되었습니다.")
        return
        
    if confirmation.lower() != 'y':
        print("작업이 사용자에 의해 취소되었습니다.")
        return

    # 3. 타겟 계정 인증
    print("\n--- 2. 타겟 YouTube 계정으로 로그인해주세요. ---")
    target_credentials = get_credentials('target_account', SCOPES_WRITE, args.client_secrets_file)
    target_youtube = build('youtube', 'v3', credentials=target_credentials)

    # 4. 타겟 계정에 구독 추가
    print("\n타겟 계정에 구독을 추가하는 중...")
    # 객체의 속성에 접근 (sub['id'] -> sub.id)
    channel_ids_to_subscribe = [sub.id for sub in source_subscriptions_data]
    subscribe_to_channels(target_youtube, channel_ids_to_subscribe)
    
    print("\n마이그레이션이 완료되었습니다.")

if __name__ == '__main__':
    main()
