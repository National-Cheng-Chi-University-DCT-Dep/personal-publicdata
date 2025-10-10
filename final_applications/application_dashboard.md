# 🎓 University Application Dashboard

**Last Updated**: 2025-10-07 13:47:05

## [OVERVIEW] Quick Overview

### 📈 Application Progress

| Status | Count | Percentage | Progress Bar |
|--------|-------|------------|--------------|
| ⚪ NOT_STARTED | 4 | 100.0% | ██████████ |

## [STATUS] Detailed School Status

| School | Country | Status | Deadline | IELTS | Budget | Priority | Confidence |
|--------|---------|--------|----------|-------|--------|----------|------------|
| ⚪ **Aalto University** | 🇫🇮 Finland | NOT_STARTED | [OK] 100d | [MEETS] MEETS | [AFFORDABLE] AFFORDABLE | 🔥 HIGH | 100% |
| ⚪ **Tallinn University of Technology** | 🇪🇪 Estonia | NOT_STARTED | [OK] 159d | [MEETS] MEETS | [AFFORDABLE] AFFORDABLE | 🔥 HIGH | 100% |
| ⚪ **Hochschule Darmstadt University of Applied Sciences** | 🇩🇪 Germany | NOT_STARTED | [OK] 159d | [MEETS] MEETS | [AFFORDABLE] AFFORDABLE | 🔥 HIGH | 100% |
| ⚪ **Linköping University** | 🇸🇪 Sweden | NOT_STARTED | [OK] 101d | [MEETS] MEETS | [AFFORDABLE] AFFORDABLE | ⚡ MEDIUM | 100% |

## 📈 Key Metrics

- **High Priority Schools**: 3/4 (75.0%)
- **IELTS Requirements Met**: 4/4 (100.0%)
- **Budget Friendly**: 4/4 (100.0%)
- **Average Confidence**: 100.0%
- **Applications Submitted**: 0
- **Decisions Pending**: 0

## [ACTIONS] Recommended Actions

- [TODO] Start work on 4 applications not yet begun

---

### [UPDATE] How to Update This Dashboard

To update application status, modify the `application_status` field in `source_data/schools.yml`:

```yaml
- school_id: "taltech"
  # ... other fields ...
  application_status: "SUBMITTED"  # NOT_STARTED, DRAFTING, SUBMITTED, DECISION_PENDING, ACCEPTED, REJECTED
```

Then regenerate the dashboard by running:
```bash
python monitoring/dashboard.py
```

*Dashboard generated at 2025-10-07 13:47:05 by Application Intelligence System v2.0*