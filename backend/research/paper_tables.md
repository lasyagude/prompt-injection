# Research Results: Sentinel Prompt Injection Middleware

## 1. Primary Model Comparison
| Configuration | Overall F1 | Precision | Recall | FPR | Escalation Stress Test |
|---|---|---|---|---|---|
| Sentinel (Hand-Tuned Baseline) | 0.8960 | 0.9337 | 0.8611 | 0.1222 | **0.8222** |
| Sentinel (Baseline + Nonlinear Gate) | 0.9209 | 0.9368 | 0.9056 | 0.1222 | **1.0000** |
| Sentinel (Logistic Regression) | 0.9239 | 0.9371 | 0.9111 | 0.1222 | **1.0000** |
| DeBERTa Only | 0.8960 | 0.9337 | 0.8611 | 0.1222 | **0.8222** |

## 2. Behavioral Features Isolation (Threshold Analysis)
| Threshold | F1 | Precision | Recall | FPR |
|---|---|---|---|---|
| 0.65 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| 0.35 | 0.1910 | 1.0000 | 0.1056 | 0.0000 |
| 0.2 | 0.4750 | 0.9500 | 0.3167 | 0.0333 |
| 0.1 | 0.7988 | 0.8405 | 0.7611 | 0.2889 |
| 0.05 | 0.8790 | 0.7911 | 0.9889 | 0.5222 |

## 3. Logistic Regression Learned Coefficients
| Feature | Learned Weight |
|---|---|
| `deberta_score` | 3.1233 |
| `role_shift_counter` | -0.3719 |
| `conversation_trajectory` | 1.5868 |
| `attack_pattern_similarity` | 1.7303 |
| `probing_similarity` | 2.9227 |
| `repetition_similarity` | 0.0000 |
| `flag_rate` | 0.0000 |
| `escalation_rate` | 1.8185 |
| `prev_risk` | 0.1316 |
| `Intercept` | -3.3166 |

## 4. Model Robustness (5-Fold Cross Validation Comparison)
| Metric | Nonlinear Gate (Mean ± Std) | Logistic Regression (Mean ± Std) |
|---|---|---|
| F1 Score | 0.9201 ± 0.0340 | 0.9321 ± 0.0320 |
| Precision | 0.9374 ± 0.0247 | 0.9390 ± 0.0239 |
| Recall | 0.9056 ± 0.0598 | 0.9278 ± 0.0598 |
| Escalation Recall | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |

## 5. Gate Threshold Sensitivity Grid
| Escalation Threshold | Topic Shift Threshold | Overall F1 | Escalation Recall |
|---|---|---|---|
| > 0.7 | > 0.6 | 0.9209 | 1.0000 |
| > 0.7 | > 0.7 | 0.9209 | 1.0000 |
| > 0.7 | > 0.8 | 0.9178 | 0.9778 |
| > 0.8 | > 0.6 | 0.9209 | 1.0000 |
| > 0.8 | > 0.7 | 0.9209 | 1.0000 |
| > 0.8 | > 0.8 | 0.9178 | 0.9778 |
| > 0.9 | > 0.6 | 0.9209 | 1.0000 |
| > 0.9 | > 0.7 | 0.9209 | 1.0000 |
| > 0.9 | > 0.8 | 0.9178 | 0.9778 |
