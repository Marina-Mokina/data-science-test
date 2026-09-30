# Results

## Part 1. Information extraction

| ID | Date | Child ID | Author | Sleep, hours | Explicit zone |
|---|---|---|---|---:|---|
| R1 | 2025-03-05 | CH-0421 | Иванова А. С. | 6.5 | — |
| R2 | 2025-03-01 | CH-0107 | Петров И. И. | 6.5 | моторика |
| R3 | 2025-01-03 | CH-0342 | — | 5.75 | — |
| R4 | 2025-03-07 | CH-0421 | Иванова | 6.5 | — |
| R5 | 2025-03-12 | CH-0107 | Петров И. И. | — | — |
| R6 | — | — | — | — | — |

## Part 2. Record classification

| ID | Expected type | Predicted type | Confidence |
|---|---|---|---:|
| R1 | observation | observation | 0.9 |
| R2 | lesson_report | lesson_report | 0.85 |
| R3 | parent_note | parent_note | 0.9 |
| R4 | observation | observation | 0.3 |
| R5 | recommendation | recommendation | 0.99 |
| R6 | observation | observation | 0.9 |

The classifier returns `unknown` when the difference between the two highest scores is below 0.15.

The threshold 0.15 was chosen to avoid forcing a classification when the scores of the two most likely record types are too close. In such cases, the system returns `unknown`.

Missing fields in Part 1 are returned as `None`.

## Part 3. Development zone analysis

| ID | Observation | Related | Confidence | Reason |
|---|---|---|---:|---|
| Z1 | отказ от еды третий день подряд | yes | 1.0 | наблюдение касается отказа от еды |
| Z2 | ударил себя по голове при смене маршрута | yes | 0.8 | ударение по голове при смене маршрута свидетельствует о проблемах в поведении при изменении условий. |
| Z3 | не отвечал на обращённую речь весь день | yes | 0.8 | наблюдение касается отсутствия реакции на речь, что относится к коммуникации |
| Z4 | закрывал уши в столовой из-за шума | yes | 0.8 | ребенок реагирует на шум, что относится к сенсорной зоне |
| Z5 | заснул только к полуночи, спал 5 часов | yes | 1.0 | наблюдение касается времени засыпания и продолжительности сна |
| Z6 | впервые сам застегнул куртку | yes | 0.9 | ребенок самостоятельно справился с задачей по застегиванию куртки |
| Z7 | не удерживает карандаш, роняет мелкие предметы | yes | 0.8 | наблюдение касается проблем с удержанием предметов, что относится к моторике |
| Z8 | плакал 20 минут без видимой причины | yes | 0.8 | ребенок плачет без видимой причины, что свидетельствует о проблеме с эмоциями |
| Z9 | поездка в центр на автобусе заняла 40 минут | no | 0.0 | это бытовое событие без явной связи с развитием |
| Z10 | родители перенесли занятие на четверг | no | 0.0 | перенос занятия не связан с развитием ребенка |
| Z11 | в кабинете меняли лампы, занятие прошло в другой комнате | no | 0.0 | наблюдение не содержит информации о развитии |
| Z12 | оформлена справка для поликлиники | no | 0.0 | без связи с зонами развития |
| Z13 | ел только жёлтую еду, остальное отодвигал | yes | 0.9 | ребенок демонстрирует предпочтение определенного цвета пищи |
| Z14 | отказался идти на занятие, потому что шёл дождь | no | 1.0 | наблюдение не касается развития ребенка |
| Z15 | был весёлым на празднике, много бегал и шумел | yes | 0.8 | ребёнок был весёлым и активным на празднике |

## Approach and fallback

Zone analysis primarily uses the local `qwen2.5:7b-instruct` model through Ollama. If the LLM is unavailable or returns an invalid response, the pipeline falls back to keyword matching. The fallback is more deterministic but less flexible for semantically complex observations.
