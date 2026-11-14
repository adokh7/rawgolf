# GolfRaw quality review: the 95 sitemap pages with no clicks

Data: Search Console, 2026-06-12 to 2026-10-18 (before the Oct 19 drop); production crawl and URL Inspection on 2026-11-14.

Nothing has been changed. Each row is a proposal.

## Summary

- **Noindex**: 1
- **Merge**: 1
- **Improve**: 6
- **Improve or noindex**: 2
- **Fix byline**: 1
- **Retitle**: 3
- **Keep + link**: 1
- **Keep**: 2
- **Keep (news archive)**: 58
- **Out of scope**: 20

## Site-level findings (these matter more than any single page)

- No copied text: the overlap inside topic clusters is 0-13%.
- Real query cannibalization is limited. The clearest case is the Tour Championship money cluster.
- Google chose not to index 2 pages after crawling them ("Crawled - currently not indexed"), and 3 sitemap URLs are unknown to Google.
- 3 articles are keyword-export or CPC analyses: content made for search engines, not for golfers.
- Most no-click pages are ordinary event news. Mass noindexing them is **not** supported by the evidence.

## Page decisions

| Decision | URL | Impr | Pos | Words | Published | Why | Top queries |
|---|---|---|---|---|---|---|---|
| Noindex | /guides-most-valuable-golf-search-cpc-data | 31 | 10.2 | 772 | 2026-08-12 | Keyword-export/CPC analysis written for SEO, not golfers (14 search-data references). | golf lookup (1 impr, pos 2) |
| Merge | /news-2026-detroit-golf-club-full-scorecard-par-70 | 0 | 0 | 898 | 2026-07-30 | Unknown to Google. Fold the scorecard into /news-2026-rocket-classic-numbers-par-4 (same event, same angle). |  |
| Improve | /news-2026-driver-fitting-guide-fitzpatrick | 275 | 8.9 | 2015 | 2026-06-26 | 275 impressions at position 8.9, 0 clicks: title and snippet mismatch. | golf driver fitting (19 impr, pos 4.6); matt fitzpatrick driver setup (13 impr, pos 7.2) |
| Improve | /golf-clubs-for-beginners | 229 | 25.4 | 1606 | 2026-06-16 | 229 impressions at position 25.4: not competitive for the head term. Needs first-hand recommendations. | best golf clubs for beginners (33 impr, pos 41.6); manual golf clubs (23 impr, pos 1.3) |
| Improve | /how-long-do-golf-clubs-last | 224 | 9.0 | 3422 | 2026-09-04 | Ranks 3-6 for lifespan questions but position 21 for the head term; 3,422 words. Tighten and lead with the answer table. | how often to upgrade golf clubs (8 impr, pos 5.8); how long do golf clubs last (7 impr, pos 21) |
| Improve | /match-play | 111 | 39.9 | 1417 | 2026-06-13 | Position 39.9. Check overlap with /match-play-vs-stroke-play before rewriting. | match play vs stroke play (5 impr, pos 52.8); stroke play vs match play (4 impr, pos 50.2) |
| Improve | /swing-speed-guide | 102 | 18.1 | 1634 |  | Position 18.1; overlaps the swing speed tool. Point it at the tool. | swing speeds and shafts (10 impr, pos 50.8); swing speed (3 impr, pos 30.7) |
| Improve | /srixon-zxi-irons-review | 0 | 0 | 2603 | 2026-09-23 | Google: Crawled - currently not indexed. A review needs first-hand testing evidence (photos, numbers, who hit them). |  |
| Improve or noindex | /news-2026-golf-ball-deals-buying-guide | 0 | 0 | 1435 | 2026-07-10 | Unknown to Google; deals content goes stale. Fold into /best-black-friday-golf-deals or refresh. |  |
| Improve or noindex | /news-2026-golf-driver-upgrades-weights | 0 | 0 | 1543 | 2026-06-26 | Google: Crawled - currently not indexed since Aug 3. |  |
| Fix byline | /equipment/golf-deals-equipment-tee-times-guide | 57 | 10.7 | 1355 | 2026-08-23 | Credited to "Marcus Keane", which the About page says doesn't exist. Switch to the desk byline. | golf price (6 impr, pos 1); discount golf balls (4 impr, pos 21.5) |
| Retitle | /news-2026-jenny-shin-womens-scottish-open-winner | 898 | 5.5 | 1006 | 2026-07-26 | 898 impressions at position 5.5 ("womens scottish open 2026" at position 1.5) and 0 clicks. Rewrite the title and description. | womens scottish open 2026 (62 impr, pos 1.5); scottish open (22 impr, pos 12.1) |
| Retitle | /news-2026-brooks-koepka-motor-city-golf-club-tgl | 315 | 2.5 | 1340 | 2026-08-27 | "tgl detroit" at position 1.2, 0 clicks. | tgl detroit (11 impr, pos 1.2); detroit tgl team roster (9 impr, pos 1) |
| Retitle | /news-2026-lexi-thompson-pregnant-baby-daughter-lpga | 274 | 6.4 | 648 | 2026-08-11 | "lexi thompson baby" at position 2.4, 0 clicks. | lexi thompson baby (66 impr, pos 2.4); lexi thompson husband and daughter (26 impr, pos 6.9) |
| Keep + link | /news-2026-rocket-classic-numbers-par-4 | 0 | 0 | 1673 | 2026-07-29 | Unknown to Google: add internal links from Rocket Classic coverage. |  |
| Keep | /news-2026-raw-golf-honest-practice-guide | 59 | 7.9 | 1704 | 2026-07-14 | Brand/manifesto page. | raw golf (11 impr, pos 5.7); rraw golf (1 impr, pos 8) |
| Keep | /raw-golf-mindset | 46 | 7.5 | 1723 |  | Brand/manifesto page. | raw swing (3 impr, pos 4.3); raw golf (2 impr, pos 11) |
| Keep (news archive) | /news-2026-liv-bedminster-purse-unknown | 740 | 8.4 | 1288 | 2026-08-06 | Event coverage that served its week; no duplicate text or query conflict found. | liv golf new york purse (151 impr, pos 10.2); liv golf bedminster prize money (18 impr, pos 8.5) |
| Keep (news archive) | /news-2026-scheffler-mcilroy-bmw-championship-tee-times | 460 | 17.6 | 994 | 2026-08-20 | Event coverage that served its week; no duplicate text or query conflict found. | mcilroy tee time (22 impr, pos 22.2); what time does rory mcilroy tee off today (16 impr, pos 19.9) |
| Keep (news archive) | /news-2026-open-joe-dean-qualifier | 407 | 8.2 | 1290 | 2026-07-14 | Event coverage that served its week; no duplicate text or query conflict found. | joe-dean (1 impr, pos 4); joe dean withdrawal (1 impr, pos 14) |
| Keep (news archive) | /news-2026-evian-championship-haeran-ryu-60 | 331 | 8.4 | 2014 | 2026-07-12 | Event coverage that served its week; no duplicate text or query conflict found. | evian cawan (7 impr, pos 60.7); evian low (2 impr, pos 18.5) |
| Keep (news archive) | /news-2026-amundi-evian-championship-iwai-korda | 307 | 9.5 | 1235 | 2026-07-10 | Event coverage that served its week; no duplicate text or query conflict found. | 2026 evian championship final leaderboard korean players 2026 (2 impr, pos 10); 2026 evian championship final korean players leaderboard (2 impr, pos 11) |
| Keep (news archive) | /news-2026-dechambeau-liv-golf-one-more-shot | 290 | 6.5 | 1062 | 2026-08-21 | Event coverage that served its week; no duplicate text or query conflict found. | bryson dechambeau hopes liv golf receives another chance amid uncertainty (21 impr, pos 2); bryson dechambeau liv golf 2026 (3 impr, pos 13.3) |
| Keep (news archive) | /haeran-ryu-outplays-nelly-korda-aig-womens-open | 279 | 7.0 | 2005 | 2026-07-30 | Event coverage that served its week; no duplicate text or query conflict found. | 유해란 aig 여자오픈 1라운드 경기 결과와 메이저 3연승 가능성 알려줘 (1 impr, pos 2); what did nelly korda shoot today (1 impr, pos 1) |
| Keep (news archive) | /news-2026-matt-mcquillan-obituary-pga-tour | 250 | 8.1 | 579 | 2026-08-07 | Event coverage that served its week; no duplicate text or query conflict found. | matt mcquillan (204 impr, pos 7.0); matthew mcquillan (7 impr, pos 1.9) |
| Keep (news archive) | /news-2026-travelers-championship-round-1-recap | 245 | 8.9 | 903 | 2026-06-26 | Event coverage that served its week; no duplicate text or query conflict found. | eric cole recent golf performance 2026 (12 impr, pos 8.9); eric cole recent performance travelers championship (8 impr, pos 10.2) |
| Keep (news archive) | /pga-2026-travelers-championship-preview | 238 | 31.0 | 1404 | 2026-06-23 | Event coverage that served its week; no duplicate text or query conflict found. | travelers championship 2026 (34 impr, pos 49.6); travelers tournament 2026 (19 impr, pos 21.1) |
| Keep (news archive) | /news-2026-scottie-scheffler-misses-first-cut-in-four-years | 211 | 9.8 | 1459 | 2026-07-10 | Event coverage that served its week; no duplicate text or query conflict found. | scottie scheffler missed cut streak (4 impr, pos 40.8); when is the last time scottie scheffler missed a cut (1 impr, pos 44) |
| Keep (news archive) | /news-2026-tiger-woods-return-travelers | 190 | 10.0 | 1380 | 2026-06-23 | Event coverage that served its week; no duplicate text or query conflict found. | is tiger woods playing in the travelers (10 impr, pos 10.4); what did tiger woods do (6 impr, pos 14) |
| Keep (news archive) | /news-2026-wyndham-clark-gary-woodland-bmw-championship-recap | 188 | 8.7 | 1436 | 2026-08-23 | Event coverage that served its week; no duplicate text or query conflict found. | woodland clark (2 impr, pos 4.5); who won the bmw championship 2026 (2 impr, pos 49) |
| Keep (news archive) | /news-2026-travelers-betting-preview | 170 | 9.8 | 1531 | 2026-06-25 | Event coverage that served its week; no duplicate text or query conflict found. | travelers championship 2026 odds (3 impr, pos 40.7); travelers preview (1 impr, pos 28) |
| Keep (news archive) | /news-2026-tommy-fleetwood-travelers-return | 169 | 9.6 | 1166 | 2026-06-27 | Event coverage that served its week; no duplicate text or query conflict found. | tommy fleetwood travelers championship (14 impr, pos 10.1); wyndham clark age (1 impr, pos 2) |
| Keep (news archive) | /news-2026-liv-golf-michigan-martin-kaymer | 166 | 8.4 | 1493 | 2026-07-22 | Event coverage that served its week; no duplicate text or query conflict found. | why is the liv golf season finale in michigan facing cancellation? (59 impr, pos 4.2); why is the liv golf finale in michigan facing cancellation and what did martin kaymer say? (11 impr, pos 6) |
| Keep (news archive) | /news-2026-harry-kane-donald-trump-golf-round | 166 | 10.4 | 1207 | 2026-07-12 | Event coverage that served its week; no duplicate text or query conflict found. | harry kane palm beach (4 impr, pos 13); harry kane played golf with donald trump 2026 (2 impr, pos 7.5) |
| Keep (news archive) | /news-2026-hovland-tie-for-lead-tour-championship | 163 | 8.2 | 1457 | 2026-08-29 | Event coverage that served its week; no duplicate text or query conflict found. | viktor hovland (3 impr, pos 1.7); who is leading the tour championship today (1 impr, pos 1) |
| Keep (news archive) | /news-2026-bryce-waters-odessa-college-golf-coach | 149 | 10.3 | 779 | 2026-06-26 | Event coverage that served its week; no duplicate text or query conflict found. | bryce waters (8 impr, pos 8.9); bryce waters golf (7 impr, pos 9.6) |
| Keep (news archive) | /mcilroy-keep-heads-down-trump-irish-open-doonbeg | 147 | 7.2 | 1380 | 2026-09-08 | Event coverage that served its week; no duplicate text or query conflict found. | rory mcilroy interview (1 impr, pos 7); doonbeg park and ride (1 impr, pos 2) |
| Keep (news archive) | /lpga-2026-nelly-korda-hazeltine-preview | 128 | 7.7 | 1111 | 2026-06-22 | Event coverage that served its week; no duplicate text or query conflict found. | lpga hazeltine (4 impr, pos 12.5); nelly korda stock yardages 2026 (1 impr, pos 44) |
| Keep (news archive) | /news-2026-liv-golf-bedminster-crushers-six-over-par | 124 | 6.9 | 746 | 2026-08-10 | Event coverage that served its week; no duplicate text or query conflict found. | recent golf news august 2026 (2 impr, pos 3.5); liv golf bedminster results (2 impr, pos 10) |
| Keep (news archive) | /news-2026-bmw-championship-round-3-scores-odds-recap | 121 | 12.1 | 1782 | 2026-08-23 | Event coverage that served its week; no duplicate text or query conflict found. | 2026 bmw championship third round (8 impr, pos 9.6); bmw championship 2026 round 3 (6 impr, pos 10.7) |
| Keep (news archive) | /news-2026-brian-harman-putter-struggle-wagner | 120 | 8.8 | 831 | 2026-08-16 | Event coverage that served its week; no duplicate text or query conflict found. | brian harman pga tour bubble (30 impr, pos 9.8); what putter does brian harman use (10 impr, pos 15.9) |
| Keep (news archive) | /news-2026-brian-rolapp-pga-commissioner | 114 | 9.8 | 1384 | 2026-06-24 | Event coverage that served its week; no duplicate text or query conflict found. | brian rolapp (12 impr, pos 3.7); pga tour commissioner (2 impr, pos 22) |
| Keep (news archive) | /news-2026-ryan-fox-open-22-seconds | 109 | 7.8 | 1448 | 2026-07-21 | Event coverage that served its week; no duplicate text or query conflict found. | ryan fox 22 seconds (3 impr, pos 12); claret jug (3 impr, pos 1) |
| Keep (news archive) | /news-2026-haeran-ryu-aig-womens-open | 107 | 5.9 | 1679 | 2026-07-30 | Event coverage that served its week; no duplicate text or query conflict found. | why (1 impr, pos 10) |
| Keep (news archive) | /news-2026-tour-championship-final-round-hovland-leads | 105 | 7.5 | 854 | 2026-08-30 | Event coverage that served its week; no duplicate text or query conflict found. | tour final (2 impr, pos 5.5); tour round (1 impr, pos 34) |
| Keep (news archive) | /news-2026-bryson-dechambeau-week-after-the-open | 94 | 5.6 | 1873 | 2026-07-27 | Event coverage that served its week; no duplicate text or query conflict found. | brooks koepka (6 impr, pos 4.5); scottie scheffler (4 impr, pos 5.5) |
| Keep (news archive) | /news-2026-aussies-kiwis-ryan-fox-scottish-open | 90 | 9.8 | 1322 | 2026-07-23 | Event coverage that served its week; no duplicate text or query conflict found. | minjee lee (1 impr, pos 10); golfer ryan fox homecoming (1 impr, pos 10) |
| Keep (news archive) | /news-2026-solheim-cup-dewi-weber-dutch-eligibility-let | 81 | 7.3 | 689 | 2026-08-11 | Event coverage that served its week; no duplicate text or query conflict found. | dewi weber solheim cup eligibility (11 impr, pos 4.6); dewi weber ranking (7 impr, pos 8.9) |
| Keep (news archive) | /us-open-round-2-highlights | 78 | 14.4 | 1508 | 2026-06-20 | Event coverage that served its week; no duplicate text or query conflict found. | us open round 2 highlights (4 impr, pos 18.2); us open round 2 (3 impr, pos 38) |
| Keep (news archive) | /news-2026-herbert-burns-62-record-birkdale | 77 | 8.3 | 1500 | 2026-07-17 | Event coverage that served its week; no duplicate text or query conflict found. | herbert, burns match major record with 62s at open championship (2 impr, pos 27.5); burns record (1 impr, pos 10) |
| Keep (news archive) | /news-2026-brooke-henderson-chases-major-sahalee | 75 | 10.2 | 1475 | 2026-06-28 | Event coverage that served its week; no duplicate text or query conflict found. | sahalee name meaning (10 impr, pos 10.9); how many majors does brooke henderson have (3 impr, pos 10.3) |
| Keep (news archive) | /news-2026-hovland-scheffler-travelers-round3 | 67 | 10.0 | 1401 | 2026-06-28 | Event coverage that served its week; no duplicate text or query conflict found. | yes (1 impr, pos 10); book three of the travelers (1 impr, pos 42) |
| Keep (news archive) | /news-2026-scottie-scheffler-final-press-conference-answer | 66 | 5.8 | 994 | 2026-08-30 | Event coverage that served its week; no duplicate text or query conflict found. | scottie scheffler press conference (6 impr, pos 16.7); scottie scheffler press conference today (2 impr, pos 8.5) |
| Keep (news archive) | /news-2026-lucas-herbert-liv-golf-uk-61 | 64 | 8.6 | 1289 | 2026-07-24 | Event coverage that served its week; no duplicate text or query conflict found. | lucas herbert liv golf round (1 impr, pos 11) |
| Keep (news archive) | /news-2026-brooks-koepka-pga-tour-return-season-verdict | 53 | 15.8 | 757 | 2026-08-11 | Event coverage that served its week; no duplicate text or query conflict found. | brooks koepka next tournament (3 impr, pos 1); did brooks koepka make the cut today (2 impr, pos 35.5) |
| Keep (news archive) | /news-2026-mcilroy-brutal-dechambeau-verdict | 52 | 10.6 | 1019 | 2026-07-18 | Event coverage that served its week; no duplicate text or query conflict found. | bryson dechambeau (4 impr, pos 1); rory mcilroy bryson dechambeau (1 impr, pos 1) |
| Keep (news archive) | /news-2026-us-womens-amateur-match-play-malixi | 46 | 6.2 | 1165 | 2026-08-08 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /news-2026-wyndham-championship-odds-day-bradley | 44 | 18.3 | 1123 | 2026-08-04 | Event coverage that served its week; no duplicate text or query conflict found. | wyndham championship odds (12 impr, pos 30.3); tour championship odds (4 impr, pos 14.5) |
| Keep (news archive) | /news-2026-travelers-championship-signature-events | 42 | 7.6 | 1276 | 2026-08-06 | Event coverage that served its week; no duplicate text or query conflict found. | travelers signature event (1 impr, pos 4); is the travellers a signature event (1 impr, pos 1) |
| Keep (news archive) | /news-2026-fleetwood-birkdale-open-round-3 | 40 | 10.2 | 929 | 2026-07-18 | Event coverage that served its week; no duplicate text or query conflict found. | tommy fleetwood scorecard today (1 impr, pos 1) |
| Keep (news archive) | /us-open-round-1-shinnecock | 40 | 10.9 | 1696 | 2026-06-19 | Event coverage that served its week; no duplicate text or query conflict found. | wyndham clark record (1 impr, pos 24); us open round 1 results (1 impr, pos 27) |
| Keep (news archive) | /us-open-2026-clark-on-the-brink | 39 | 11.8 | 1296 | 2026-06-21 | Event coverage that served its week; no duplicate text or query conflict found. | wyndham clark fan backlash (1 impr, pos 2); have they ever played together (1 impr, pos 6) |
| Keep (news archive) | /news-2026-trump-east-potomac-fazio-major | 35 | 11.2 | 1459 | 2026-06-29 | Event coverage that served its week; no duplicate text or query conflict found. | east potomac golf (5 impr, pos 13); tom fazio son (1 impr, pos 11) |
| Keep (news archive) | /news-2026-collin-morikawa-61-travelers-weather | 28 | 15.9 | 1181 | 2026-06-29 | Event coverage that served its week; no duplicate text or query conflict found. | collin morikawa travelers championship 61 (4 impr, pos 1) |
| Keep (news archive) | /us-open-round-2-shinnecock | 25 | 10.4 | 1636 | 2026-06-20 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /morikawa-61-travelers-championship-2026 | 24 | 4 | 1019 | 2026-08-15 | Event coverage that served its week; no duplicate text or query conflict found. | collin morikawa travelers championship 2026 (1 impr, pos 1); collin morikawa (1 impr, pos 1) |
| Keep (news archive) | /news-2026-xander-schauffele-jackson-koivun-reaction | 23 | 6.2 | 1599 | 2026-07-29 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /news-2026-liv-golf-250m-investment-rescue | 22 | 12.2 | 1815 | 2026-07-30 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /news-2026-dechambeau-faldo-suber-birkdale | 19 | 11.6 | 1341 | 2026-07-16 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /news-2026-cameron-smith-bedminster-liv-winning-margin | 17 | 7.9 | 871 | 2026-08-07 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /news-2026-rory-bryson-open-verdict | 16 | 7.6 | 1122 | 2026-07-19 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /news-2026-tiger-woods-pleads-guilty-reckless-driving-jupiter-island | 11 | 12.9 | 1718 | 2026-09-02 | Event coverage that served its week; no duplicate text or query conflict found. | woods sentence (1 impr, pos 59) |
| Keep (news archive) | /news-2026-fleetwood-open-birkdale | 9 | 16.4 | 1323 | 2026-07-21 | Event coverage that served its week; no duplicate text or query conflict found. | royal birkdale (1 impr, pos 19) |
| Keep (news archive) | /news-2026-scheffler-mcilroy-birkdale-press-conference | 4 | 7.5 | 1471 | 2026-07-15 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Keep (news archive) | /us-open-2026-final-round-live-updates | 0 | 0 | 1483 | 2026-06-21 | Event coverage that served its week; no duplicate text or query conflict found. |  |
| Out of scope | /pga-tour | 810 | 30.1 | 9316 |  | Utility, hub or tool page; not meant to win searches. | pga tour news (38 impr, pos 56.6); pga news (28 impr, pos 39.9) |
| Out of scope | /tools-tilt-meter | 182 | 8.6 | 1058 |  | Utility, hub or tool page; not meant to win searches. | tilt score (4 impr, pos 5.5); amateur blow (3 impr, pos 15.3) |
| Out of scope | /gear | 109 | 27.7 | 2374 |  | Utility, hub or tool page; not meant to win searches. | stiff arm golf (5 impr, pos 63.4); golfw (4 impr, pos 93.2) |
| Out of scope | /full-board | 96 | 18.8 | 309 |  | Utility, hub or tool page; not meant to win searches. | jon rahm ranking (13 impr, pos 69.6); golf ratings (2 impr, pos 31.5) |
| Out of scope | /tools-field-reader | 81 | 19.9 | 729 |  | Utility, hub or tool page; not meant to win searches. | course fit tool (13 impr, pos 7.5); course fit (12 impr, pos 6.3) |
| Out of scope | /about | 33 | 4.3 | 533 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /analysis | 25 | 6.4 | 343 |  | Utility, hub or tool page; not meant to win searches. | golf swing analysis and tour player stats -site:youtube.com -site:reddit.com -site:x.com -site:twitter.com -site:facebook.com -site:instagram.com -site:tiktok.com -site:linkedin.com -site:pinterest.com -site:nytimes.com -site:wsj.com -site:yelp.com -site:rottentomatoes.com (2 impr, pos 1); golf analyseparalyse (1 impr, pos 47) |
| Out of scope | /vault | 23 | 6.4 | 189 |  | Utility, hub or tool page; not meant to win searches. | the vault golf (1 impr, pos 10) |
| Out of scope | /contact | 23 | 57.5 | 371 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /vintage-golf-history | 23 | 8.7 | 210 |  | Utility, hub or tool page; not meant to win searches. | vintage golfer (1 impr, pos 21); vintage golf magazines (1 impr, pos 21) |
| Out of scope | /tools-tendency-engine | 20 | 6.7 | 786 |  | Utility, hub or tool page; not meant to win searches. | this is not strokes (1 impr, pos 1) |
| Out of scope | /privacy | 12 | 5.5 | 936 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /tools-coach-report | 9 | 5.9 | 607 |  | Utility, hub or tool page; not meant to win searches. | what carry distance variance is acceptable during fitting? (1 impr, pos 1) |
| Out of scope | /corrections | 7 | 5.9 | 433 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /tools-standing-order | 6 | 4.5 | 1204 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /lpga-tour | 0 | 0 | 299 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /players | 0 | 0 | 162 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /terms | 0 | 0 | 1069 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /press | 0 | 0 | 539 |  | Utility, hub or tool page; not meant to win searches. |  |
| Out of scope | /pro | 0 | 0 | 319 |  | Utility, hub or tool page; not meant to win searches. |  |

## Also flagged (just outside the zero-click set)

| Decision | URL | Clicks / impr (before the drop) | Why |
|---|---|---|---|
| Noindex | /news-2026-golf-deals-means-travel | 1 / 64 | Keyword-export analysis (15 search-data references). |
| Noindex | /news-2026-golf-pga-australia-search-demand | 1 / 103 | Keyword-file analysis (16 references). Move the real Australian PGA event facts into event coverage. |
| Rewrite or noindex | /news-2026-what-beginners-actually-search | 1 / 39 | Framed around search data. Rewrite as a plain beginner guide, or noindex. Note that /what-beginners-actually-search 308-redirects here. |
| Merge | /news-2026-tour-championship-points-and-payouts | 0 / 29 on shared queries | Competes with /news-2026-tour-championship-prize-money-payout (position 50.9 vs 11.9). 301 there. |
| Merge | /news-2026-tour-championship-purse-east-lake | some clicks | Same intent as the prize-money page ("tour championship payout"): 159 vs 7,404 impressions. 301 there after moving any unique facts across. |
| Fix byline | /rules/golf-tournaments-rules-formats-tax-guide | n/a | Credited to "Marcus Keane", which the About page says doesn't exist. |
