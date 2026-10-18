# DPDP Act 2023 Compliance & Data Inventory Mapping

How EasyDP Local PII Scanner maps to Data Fiduciary statutory obligations under India's **Digital Personal Data Protection (DPDP) Act, 2023**.

---

## 1. Statutory Data Inventory Mapping (DIM)

Under the DPDP Act, organizations acting as **Data Fiduciaries** must know what personal data they process, where it resides, and the purpose of retention.

The scanner automatically generates structured inventories corresponding to:
- **DIM-01 (Data Discovery & Classification)**: Identifying all file paths and systems holding personal data.
- **DIM-03 (Data Minimization & Category Register)**: Classifying records into *Identity*, *Financial*, and *Contact* categories.
- **DIM-04 (Storage & Retention Governance)**: Flagging files that have exceeded retention periods (>1 year, >3 years old).

---

## 2. Sole Proprietors vs. Corporate Entities in B2B Data

Under Section 2(t) of the DPDP Act 2023:
> *"Personal data means any data about an individual who is identifiable by or in relation to such data."*

In Indian business commerce:
- **Incorporated Companies (Pvt Ltd / Ltd)**: PAN 4th character is `'C'`. Pure corporate data is outside DPDP personal data scope.
- **Sole Proprietorships**: PAN 4th character is `'P'`. A sole proprietor's business GSTIN and PAN belong to a natural person. Therefore, **sole proprietorship B2B vendor lists are governed by the DPDP Act**.
- **Directors & Authorized Signatories**: B2B contracts, KYC documents, and board resolutions that include personal Aadhaar or mobile numbers of company directors are protected personal data.

The scanner automatically classifies the 4th character of PAN cards to help compliance teams distinguish between corporate entities and individual proprietors.

---

## 3. Data Retention & Purpose Limitation (Section 8(7))

Section 8(7) of the DPDP Act requires Data Fiduciaries to erase personal data as soon as the specified purpose is satisfied, or when retention is no longer necessary for legal or business purposes.

The scanner identifies:
- Files modified **> 1 year ago**
- Files modified **> 3 years ago**

Files sitting forgotten in `Downloads/` or `Desktop/` past statutory limitation periods represent significant regulatory exposure during data breach inquiries.
