- 현재 jnj-android는 ubuntu xfce 환경에서 android 앱을 자동화 하는 범용 프로젝트입니다.
- 우선 RoK 앱에 대한 자동화를 구현 중에 있지만, 다른 앱의 사용도 염두에 두어야 합니다.
- backend에서는 waydroid 사용에 관련된 코드(adb 제어, waydroid 실행, 중지 등)와 RoK 게임 관련 코드가 폴더 단위에서 분리되어 있어합니다
- android 관련된 폴더에서도 adb 제어(실행, 중지, 실행 확인 등), playstore 관련 내용(로그인, ...), waydroid 제어(실행, 중지, 실행 확인 등) 등도 파일 단위로 분리되어야 합니다.
- Rok 게임에 관련된 폴더에서도 Rok 앱 실행/진입, RoK 내 미션.액션 관련된 내용은 파일 단위에서 분리되어야 합니다.
- /home/sam/JnJ/developments/waydroid_script

- /home/sam/JnJ/developments/jnj-android/emulator 디렉토리에 내용과 /home/sam/JnJ/developments/waydroid_script 디렉토리의 내용과 중복되어 있는지 확인후,
- 기존 내용 중 중복되는 내용은 삭제하고 기존 내용은 /home/sam/JnJ/developments/jnj-android/emulator/legacy 로 모두 이동하고,
- /home/sam/JnJ/developments/waydroid_script 를 
/home/sam/JnJ/developments/jnj-android/emulator/waydroid 로 이동합니다.
  - 다만 /home/sam/JnJ/developments/waydroid_script 에 있던 python 파일들은 /home/sam/JnJ/developments/jnj-android/backend/python/src/utils/waydroid로 이동해야 겠네요.

# 방법 2: 직접 waydroid 디렉토리로
mv /home/sam/JnJ/developments/waydroid_script /home/sam/JnJ/developments/jnj-android/waydroid