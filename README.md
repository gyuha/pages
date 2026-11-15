# pages

GitHub Pages로 만든 사이트를 카테고리별로 모아 보여 주는 페이지입니다.

- 사이트: <https://gyuha.com/pages/>
- 사이트 목록: [`_data/sites.yml`](_data/sites.yml)
- 스타일: [`assets/css/style.scss`](assets/css/style.scss)

## 새 사이트 추가하기

`_data/sites.yml`의 해당 카테고리 `sites` 목록에 항목을 추가합니다.

```yaml
- name: 사이트 이름
  url: https://gyuha.com/example/
  desc: 한 줄 설명.
  tag: Tech
```

## 로컬에서 미리 보기

```sh
gem install jekyll jekyll-theme-minimal
jekyll serve
```

기본 주소는 <http://localhost:4000>입니다.
