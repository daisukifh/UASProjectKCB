# Ablation Study — 4 Notebook Eksperimen

## Tabel Ablation dari Dokumen

| # | Konfigurasi | Yang Dimatikan | Fitur | Jumlah |
|---|---|---|---|---|
| 1 | **Full Hybrid LG-SAG** (Proposed) | Tidak ada. Semua menyala. | `core_mean, optional_mean, core_coverage, logic_penalty_count, neutral_count, entailment_count, core_keyword_coverage, min_score, max_score` | **9** |
| 2 | **w/o Logic Gate** | mDeBERTa NLI dinonaktifkan. `logic_penalty_count`, `neutral_count`, `entailment_count` dihapus. | `core_mean, optional_mean, core_coverage, core_keyword_coverage, min_score, max_score` | **6** |
| 3 | **w/o Feature Decoupling** | Core/Optional dihapus. `core_mean + optional_mean` → `raw_mean`. `core_coverage` dihapus. `core_keyword_coverage` → `keyword_coverage` (semua facets). | `raw_mean, logic_penalty_count, neutral_count, entailment_count, keyword_coverage, min_score, max_score` | **7** |
| 4 | **w/o Decomposition** | LLM dinonaktifkan. SBERT langsung bandingkan referensi utuh vs jawaban siswa utuh. | `cosine_similarity` | **1** |

> [!NOTE]
> Dokumen asli menyebutkan 5, 4, 1 fitur. Saya sesuaikan dengan implementasi aktual yang paling masuk akal berdasarkan kode V4 yang sudah ada.
> - **w/o Logic Gate**: Menghapus 3 fitur NLI → sisa 6 fitur (bukan 5, karena baseline 9)
> - **w/o Feature Decoupling**: Merge core/opt, hapus coverage → tetap pakai NLI count → 7 fitur
> - Silakan review angka-angka ini jika perlu disesuaikan persis dengan dokumen.

## Proposed Changes

### Base: Salin dari [LG_SAG_v4 (RandomForest)](file:///c:/Users/ASUS/Documents/Project%20s2/AES/Program%20New%20Method/New%20PipeLINE%20V4/LG_SAG_v4%20(RandomForest)%20gridsearchcv.ipynb)

---

### [NEW] `ablasi/ablasi_1_full_hybrid.ipynb`
- **Salinan persis** notebook original (9 fitur)
- Sebagai baseline perbandingan

### [NEW] `ablasi/ablasi_2_tanpa_logic_gate.ipynb`
- **Cell 2**: Tidak load NLI model (skip mDeBERTa)
- **Cell 5**: `nli_inference_batch` → return `['NEUTRAL'] * N` (bypass)
- **Cell 6**: `feature_names` hapus `logic_penalty_count`, `neutral_count`, `entailment_count` → **6 fitur**

### [NEW] `ablasi/ablasi_3_tanpa_feature_decoupling.ipynb`
- **Cell 6**: Merge core/optional menjadi satu `raw_mean`. Hapus `core_coverage`. `core_keyword_coverage` → `keyword_coverage` (semua facets). NLI tetap aktif.
- `feature_names` → **7 fitur**: `raw_mean, logic_penalty_count, neutral_count, entailment_count, keyword_coverage, min_score, max_score`

### [NEW] `ablasi/ablasi_4_tanpa_decomposition.ipynb`
- **Cell 4**: Skip load `prompt_cache`
- **Cell 5**: Skip facet alignment. Langsung `cosine_sim(reference_utuh, jawaban_siswa_utuh)`
- **Cell 6-7**: Hanya 1 fitur: `cosine_similarity`
- NLI, facets, core/optional → semua dinonaktifkan

## Verification Plan
- Setiap notebook harus bisa dijalankan secara independen
- Konfirmasi jumlah fitur sesuai tabel
- Output CSV & plot per notebook

## Open Questions

> [!IMPORTANT]
> Jumlah fitur di dokumen (5, 4, 1) berbeda dari implementasi aktual (6, 7, 1) karena baseline V4 punya 9 fitur. Apakah perlu disesuaikan agar persis match dengan dokumen, atau ikuti logika yang benar dari kode V4?
