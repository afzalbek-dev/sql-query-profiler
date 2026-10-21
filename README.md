# 🔍 SQL Query Profiler

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

Python ilovalari (FastAPI, Django, Flask, SQLAlchemy, Tortoise-ORM) uchun SQL so'rovlarini statik tahlil qilish, eng xavfli va samarasiz anti-patternlarni (**N+1 Muammosi**, `SELECT *`, cheklanmagan `LIMIT`, implicit Dekart ko'paytmasi) aniqlash hamda profayling hisobotini tuzish vositasi.

---

## 🌟 Qanday Anti-Patternlarni Aniqlaydi?

- **N+1 Query Detection:** Sikl ichida takroriy yuborilayotgan bir xil shablonli so'rovlarni avtomatik aniqlaydi.
- **`SELECT *` Taqiqlash (`PERF001`):** Keraksiz ustunlarni yuklab xotira va tarmoqni band qilishni ogohlantiradi.
- **Cheklovsiz SELECT (`PERF002`):** `LIMIT`siz so'rovlar millionlab qatorlarni xotiraga tortib serverni to'xtatish xavfini bildiradi.
- **Boshlanuvchi Wildcard (`PERF003`):** `LIKE '%matn'` indekslarni o'chirib, to'liq jadvalni kezishga (Full Table Scan) majbur qilishini aniqlaydi.
- **Xavfli UPDATE/DELETE (`DANG001`):** `WHERE` shartisiz butun jadvalni tozalab yuboruvchi xavfli so'rovlarni qizil belgi bilan bloklaydi.
- **Implicit Dekart Ko'paytmasi (`PERF004`):** `FROM a, b` kabi xavfli ko'paytmalarni aniqlaydi.

---

## 🚀 O'rnatish

```bash
git clone https://github.com/afzalbek-dev/sql-query-profiler.git
cd sql-query-profiler
pip install .
```

---

## 🛠️ Foydalanish

### 1. Bitta so'rovni tahlil qilish (Static Linting)

```python
from sql_profiler import SQLAnalyzer

analyzer = SQLAnalyzer()
result = analyzer.analyze("SELECT * FROM users WHERE email LIKE '%@gmail.com'")

for issue in result.issues:
    print(f"[{issue.severity.value}] {issue.code} - {issue.title}: {issue.message}")
```

### 2. Sessiya Profayling va N+1 Muammosini Topish

```python
from sql_profiler import SQLProfiler

with SQLProfiler(n_plus_one_threshold=3) as profiler:
    # Simulyatsiya: 10 ta kitob muallifini siklda chaqirish (N+1 xatosi)
    for author_id in range(10):
        profiler.record_query(f"SELECT name FROM authors WHERE id = {author_id} LIMIT 1", duration_ms=1.5)

    report = profiler.generate_report()
    if report["n_plus_one_detected"]:
        print("🚨 N+1 muammosi aniqlandi!")
        for pattern, count in report["n_plus_one_patterns"].items():
            print(f"  Takrorlanish: {count} marta -> {pattern}")
```

---

## 🧪 Testlash

```bash
python3 -m unittest discover tests -v
```

---

## 📄 Litsenziya

MIT License. Muallif: [Afzalbek](https://github.com/afzalbek-dev).
