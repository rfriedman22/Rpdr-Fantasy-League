---
title: Past Seasons
---
Here are all the seasons I have run a fantasy league for:
{% for season in site.data.seasons.leagues -%}
- [Season {{ season }}](/{{ site.data.seasons.page_dir }}/{{ season }}/)
{% endfor %}