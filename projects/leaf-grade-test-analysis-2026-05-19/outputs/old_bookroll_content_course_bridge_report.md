# Old BookRoll Content-Course Bridge

## Method
- Source tables: br_contents_belong_directory, br_contents_directory, br_contents_directory_owner.
- Candidate mapping: contents_id -> directory -> directory_owner.owner_id prefix before @ -> Moodle/score course_id.
- High confidence requires owner_id prefix to match a known score-table/Moodle course_id.

## Coverage
- Raw content-directory-owner candidate rows: 33,337
- Unique contents with one mapped score course: 6,356
- Ambiguous content-course candidate rows: 19,331
- Candidate confidence low: 7,382
- Candidate confidence high: 25,943
- Candidate confidence medium: 12

## Top Courses By Unique Mapped Contents
- 311 2020年度IEC2[高2]: 397 contents
- 39 2019年度前期数学[中3]B組: 243 contents
- 41 2019年度前期数学[中3]C組: 243 contents
- 37 2019年度前期数学[中3]A組: 239 contents
- 389 2022年度IEC2[高2]: 110 contents
- 370 2021年度数学[高1]: 105 contents
- 55 2019年度前期英語[中3]A組: 103 contents
- 57 2019年度前期英語[中3]B組: 103 contents
- 59 2019年度前期英語[中3]C組: 103 contents
- 27 2019年度前期数学[中1]B組前半: 103 contents
- 280 2020年度 教員への研修会: 103 contents
- 26 2019年度前期数学[中1]A組後半: 100 contents
- 84 2019年度前期数学[中1]C組後半: 99 contents
- 25 2019年度前期数学[中1]A組前半: 97 contents
- 29 2019年度前期数学[中1]C組前半: 97 contents
- 28 2019年度前期数学[中1]B組後半: 96 contents
- 371 2021年度IEC2[高2]: 90 contents
- 606 2024年度中学2年B組[数学]: 84 contents
- 480 2023年度中学2年B組[数学]: 83 contents
- 605 2024年度中学2年A組[数学]: 83 contents
- 593 2024年度中学1年A組[数学]: 81 contents
- 446 緒方研究室デモコース: 80 contents
- 607 2024年度中学2年C組[数学]: 78 contents
- 47 2019年度前期英語[中1]C組前半: 77 contents
- 481 2023年度中学2年A組[数学]: 75 contents
- 46 2019年度前期英語[中1]B組後半: 74 contents
- 48 2019年度前期英語[中1]C組後半: 74 contents
- 44 2019年度前期英語[中1]A組後半: 73 contents
- 45 2019年度前期英語[中1]B組前半: 72 contents
- 479 2023年度中学2年C組[数学]: 71 contents

## Interpretation
- This bridge is strong enough to test same-course old BookRoll linkage for uniquely mapped contents.
- Ambiguous contents should be excluded from same-course modeling until reviewed.
