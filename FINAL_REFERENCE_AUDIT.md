# FINAL_REFERENCE_AUDIT

Ten references. Each checked for authors, title, year, venue, volume/pages, and
whether it supports the sentence citing it. No new references introduced.

| Key | Record as printed | Verification | Supports its use? |
|---|---|---|---|
| `eltbench` | Jin, Zhu, Kang. "ELT-Bench: An end-to-end benchmark for evaluating AI agents on ELT pipelines." *Proc. VLDB Endow.* 19(2):84–98, 2025. | Confirmed: PVLDB vol.19, paper p84-jin (`vldb.org/pvldb/vol19/p84-jin.pdf`); DOI 10.14778/3773749.3773750. Issue 2 and page range match the record in the Verified paper's own bibliography. | Yes — cited for the benchmark's existence, task/model counts and column-wise scoring, all stated in that paper. |
| `eltverified` | Zanoli, Giovannini, Jin, Klimovic, Perlitz. "ELT-Bench-Verified: Benchmark quality issues underestimate AI agent capabilities." arXiv:2603.29399, 2026. | Confirmed: arXiv ID, author list and title match the paper we read. Under PVLDB submission; we cite the arXiv version, which is correct for an unpublished record. | Yes — cited for the audit finding (a third of column mismatches benchmark-attributable), the specific normalisations, and human-judgement validation. All appear in that paper. |
| `annotationerrors` | Jin, Choi, Zhu, Kang. "Pervasive annotation errors break text-to-SQL benchmarks and leaderboards." *Proc. VLDB Endow.* 19(5):931-944, 2026. | **Upgraded from arXiv to the archival version.** Confirmed from the published PDF header (`vldb.org/pvldb/vol19/p931-jin.pdf`): vol.19, no.5, pp.931-944, DOI 10.14778/3796195.3796206. PVLDB also announced it under Vol:19 No:5, and it appears in the VLDB 2026 program as an EA&B paper. | Yes — cited only for "audits of text-to-SQL benchmarks report pervasive errors that penalise correct outputs". |
| `tuya` | Tuya, Suárez-Cabal, de la Riva. "Mutating database queries." *Inf. Softw. Technol.* 49(4):398–417, 2007. | Confirmed directly from the authors' PDF: volume 49, issue 4, pages 398–417, 2007. Operator categories SC, OR (ROR/LCR/UOI/ABS/AOR/BTW/LKE), NL, IR. | Yes — cited for the conventional operator pool and for the disclosed NL/absence overlap. The NL category does mutate NULL handling, so the overlap claim is accurate. |
| `jiaharman` | Jia, Harman. "An analysis and survey of the development of mutation testing." *IEEE Trans. Softw. Eng.* 37(5):649–678, 2011. | Confirmed: DOI 10.1109/TSE.2010.62, dblp `journals/tse/JiaH11`, vol.37 no.5 pp.649–678. | Yes — cited for mutation testing as seeded faults assessing a test suite. |
| `mutationsurvey` | Papadakis, Kintis, Zhang, Jia, Le Traon, Harman. "Mutation testing advances: An analysis and survey." *Adv. Comput.* 112:275–378, 2019. | Confirmed: dblp `journals/ac/PapadakisK00TH19`; appears as "Chapter Six" in *Advances in Computers* vol.112, 2019. Printed record is accurate; the chapter designation is omitted, which is conventional. | Yes — cited alongside `jiaharman` for the same general point. |
| `kimball` | Kimball, Ross. *The Data Warehouse Toolkit*, 3rd ed. Wiley, 2013. | Standard bibliographic record; 3rd edition published 2013 by Wiley. | Yes — cited for declared grain, additive/semi-additive measures and temporal modelling, all core content of that book. |
| `codd` | Codd. "Extending the database relational model to capture more meaning." *ACM Trans. Database Syst.* 4(4):397–434, 1979. | Standard record: TODS vol.4 no.4, December 1979, pp.397–434. | Yes — cited for absence semantics under three-valued logic. Codd's RM/T paper treats missing information explicitly, so the support is direct. |
| `spider2` | Lei et al. "Spider 2.0: Evaluating language models on real-world enterprise text-to-SQL workflows." ICLR, 2025. | **Upgraded from arXiv to the archival version.** Confirmed from the ICLR 2025 proceedings entry (title, first author Fangyu Lei, full author list, ICLR 2025). | Yes — cited only as an example of an execution-based benchmark. |
| `bird` | Li et al. "Can LLM already serve as a database interface? A big bench for large-scale database grounded text-to-SQLs." NeurIPS, 2023. | Confirmed via the Verified paper's bibliography (ref [14]); NeurIPS 2023 proceedings. | Yes — same use as `spider2`. |

## Findings

- **No bibliographic errors requiring correction.**
- **Two archival upgrades applied in the final pass** (see rows above): `annotationerrors` arXiv -> PVLDB 19(5):931-944, and `spider2` arXiv -> ICLR 2025. Both verified against primary sources, not secondary listings.
- One record remains an arXiv preprint: `eltverified`. A fresh check found the March 2026 arXiv paper but no confirmed archival publication, so citing the arXiv version stays correct.
- `mutationsurvey` omits the "Chapter Six" designation. This is conventional for
  *Advances in Computers* chapters and is not an error.
- Every citation is load-bearing for the sentence that uses it; none is
  decorative, and no sentence relies on a citation that does not support it.
- References occupy well under the one-page allowance.
