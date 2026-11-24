# AGENTS.md

이 저장소는 **GitHub Pages로 만든 사이트들을 카테고리별로 모아 보여 주는 단일 페이지**입니다.

- 배포 주소: <https://pages.gyuha.com/>
- 저장소: <https://github.com/gyuha/pages>
- GitHub Pages 설정: `main` 브랜치 `/` (legacy Jekyll 빌드)
- 테마: `jekyll-theme-minimal`

## "배포해줘"라고 하면

아래 순서를 그대로 수행합니다. 사용자가 "배포해줘", "페이지 업데이트해줘", "사이트 목록 갱신해줘"라고 하면 이 절차를 의미합니다.

### 1. Pages 사이트 전체 수집

```sh
python3 scripts/discover-pages.py --check
```

이 스크립트가 하는 일:

- `gh auth token`으로 인증해 **소유한 모든 저장소**를 pagination으로 가져옵니다.
  (`gh repo list --limit 200`은 200개에서 잘리므로 쓰지 않습니다. 저장소가 300개 이상입니다.)
- 각 저장소의 `/repos/{owner}/{repo}/pages`를 조회해 **GitHub Pages가 켜진 공개 저장소**만 추립니다.
- 이 페이지 자체(`pages` 저장소)는 목록에서 제외합니다.
- `_data/sites.yml`에 이미 있는 URL인지 표시하고, `--check`를 주면 실제 접속 상태와 페이지 제목을 확인합니다.

출력에서 **NEW**(목록에 없는 새 사이트)와 **MISSING**(목록에는 있지만 Pages를 찾을 수 없는 사이트), **BROKEN**(접속 실패)을 확인합니다.

### 2. `_data/sites.yml` 갱신

- **NEW 사이트**: 실제 페이지의 `<title>`, meta description, README를 확인해 아래 형식으로 추가합니다. 추측으로 설명을 쓰지 않습니다.
- **BROKEN / MISSING 사이트**: 임의로 삭제하지 않습니다. 사용자에게 알리고 확인을 받습니다. DNS 미설정처럼 사이트 자체는 살아 있는 경우가 있습니다.
- **기존 항목**: 이름·설명·URL이 실제 페이지와 다르면 수정합니다. 단순한 오탈자 수준은 바로 고쳐도 됩니다.
- 카테고리 순서와 기존 사이트 순서는 꼭 필요할 때만 바꿉니다.

항목 형식:

```yaml
- name: 사이트 이름
  url: https://gyuha.com/example/
  desc: 한 줄 설명.
  tag: Tech
```

규칙:

- `desc`는 한국어 한 줄, 40자 안팎. 페이지의 실제 소개를 요약합니다.
- `tag`는 기술이나 성격을 나타내는 짧은 라벨입니다. (`Three.js`, `PWA`, `MCP`, `Docs` 등)
- URL은 `https://`로 통일합니다.
- **비공개 저장소는 넣지 않습니다.** 이 페이지는 공개 쇼케이스입니다.
- 새 카테고리가 필요하면 `_data/sites.yml`의 최상위 항목으로 추가합니다. `id`는 URL anchor로 쓰이므로 영문 소문자·하이픈으로 정합니다. (`blog`, `games`, `tools`, `dev`, `docs`는 기존 anchor이므로 유지)
- 새 카테고리에는 `color`를 지정합니다. 페이지의 점·태그·hover 색에 쓰입니다. 기존 색: `blog #3f6b52`, `games #a9492a`, `tools #3f5d8c`, `dev #866526`, `docs #7a4568`.
- 사이트 개수, 카테고리 개수, 카테고리 nav는 `index.md`의 Liquid가 자동 계산합니다. **숫자를 직접 고치지 않습니다.**

### 3. 로컬 빌드 확인

```sh
export PATH="$(ruby -e 'print Gem.user_dir')/bin:$PATH"

# jekyll이 없을 때만
gem install --user-install jekyll jekyll-theme-minimal

jekyll build
```

`_site/index.html`이 정상 생성되는지 확인합니다. 필요하면 로컬에서 눈으로 확인합니다.

```sh
python3 -m http.server 4173 --directory _site
```

YAML 문법 오류나 Liquid 오류가 있으면 빌드가 실패하므로, push 전에 반드시 `jekyll build`를 통과시킵니다.

### 4. 커밋과 배포

```sh
git add _data/sites.yml
git commit -m "Update site directory"
git push origin main
```

`index.md`, 스타일, 스크립트를 함께 고쳤다면 해당 파일도 add 합니다. `_site/`는 `.gitignore`에 포함되어 있으므로 커밋하지 않습니다.

### 5. 배포 완료 확인

push 후 GitHub Pages 빌드를 기다립니다.

```sh
for i in $(seq 1 30); do
  s=$(gh api repos/gyuha/pages/pages -q '.status' 2>/dev/null)
  echo "$s"
  [ "$s" = "built" ] && break
  sleep 5
done
```

그다음 실제 페이지를 확인합니다.

```sh
curl -sI https://pages.gyuha.com/
curl -s https://pages.gyuha.com/ | grep -o '<title>[^<]*</title>'
```

- HTML 캐시 때문에 방금 배포한 내용이 안 보이면 `https://pages.gyuha.com/?v=2`처럼 쿼리를 붙여 확인합니다.
- 새 사이트 링크가 모두 200인지 확인합니다. 실패한 링크는 결과 보고에 적습니다.

### 6. 결과 보고

사용자에게 다음을 간단히 보고합니다.

- 추가한 사이트와 카테고리
- 수정·삭제한 항목 (삭제는 사전 확인을 받은 경우만)
- 접속 실패 또는 DNS 문제가 있는 링크
- 배포 주소: <https://pages.gyuha.com/>

## 파일 구조

| 파일 | 역할 |
|---|---|
| `index.md` | 페이지 본문. 카테고리·카드·검색 UI를 Liquid로 렌더링 |
| `_data/sites.yml` | **사이트 목록 데이터. 콘텐츠 수정은 여기서만** |
| `assets/css/style.scss` | 스타일. 테마 CSS를 import한 뒤 덮어씀 |
| `assets/js/filter.js` | 검색, 카드 등장, sticky 툴바 |
| `scripts/discover-pages.py` | Pages 사이트 수집·비교 스크립트 |
| `_config.yml` | Jekyll 설정 |
| `README.md` | 사람이 보는 간단한 안내 |

## 주의사항

- `_config.yml`의 `theme`를 바꾸면 `assets/css/style.scss`의 `@import "{{ site.theme }}"`도 함께 확인합니다.
- 커스텀 도메인 `pages.gyuha.com`으로 서비스되므로 자산 경로는 `/assets/...`가 됩니다. `relative_url` 필터를 유지합니다.
- `CNAME` 파일은 `pages.gyuha.com`이어야 하며, Cloudflare DNS에 `pages` CNAME → `gyuha.github.io`(프록시 끔) 레코드가 있어야 합니다. 도메인을 바꾸면 이 두 곳을 함께 수정합니다.
- `jekyll-theme-minimal`의 기본 `footer`는 fixed 사이드바 위치라 CSS에서 static으로 덮어쓰고 있습니다. 이 override를 지우면 footer가 본문 위에 겹칩니다.
- GitHub Pages의 legacy Sass 빌드는 `@supports selector(...)`를 처리하지 못해 빌드가 10분 넘게 멈추다 실패합니다. 이 문법을 쓰지 말고, 스크롤바 스타일은 `::-webkit-scrollbar` 규칙을 그대로 둡니다.
- `color-mix()`, `clamp()`, `min()`, `:focus-visible` 등 최신 CSS는 사용해도 되지만, 빌드가 이상하게 오래 걸리면 먼저 Sass가 해석하는 문법을 의심합니다.
- 저장소가 많아 API 호출 수가 많습니다. 인증 토큰은 `gh auth token`을 사용하고, 스크립트의 동시 요청 수를 과도하게 올리지 않습니다.
- 비밀값, 토큰, 비공개 저장소 정보를 이 저장소에 커밋하지 않습니다.
