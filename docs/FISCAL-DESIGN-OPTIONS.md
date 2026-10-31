# Fiscal design options: Tang and Song framework

Updated: **2026-10-28**. Status: **Historical alternatives retained for reference. Revenue custody is now the user's preferred working direction; engine mechanism and implementation remain pending.**

Latest proposal: [Revenue common fund, allocations, programme and safeguards](REVENUE-COMMON-FUND-DESIGN.md). The comparisons below record the exploration that informed this direction.

User preference: explore alternatives before selecting a sufficient, historically grounded design. Support both Tang and Song settings. Revenue custody of a shared ministerial fund is acceptable as a candidate. The imperial public treasury should remain distinct from the proposed ministerial fund; personal gold and provincial treasuries are outside that merger.

Technical evidence remains in [Shared ministerial treasury feasibility](SHARED-MINISTERIAL-TREASURY-FEASIBILITY.md). That audit establishes scriptable transfers and the unresolved native payer/operating-advance problem. It does not select the final institutions.

## Historical findings

### Fiscal coordination can coexist with several accounts

Late Tang prefectural finances included retained tax revenue, public-use funds and granaries. Early Northern Song centralization recovered revenues beyond obligatory local expenses. This supports variation in central control and remittance obligations; it does not establish one cash account shared by nine departments. See Watanabe Shin'ichiro, translated by Matthew Fraleigh, [Local Financial Administration in the Latter Half of the Tang Dynasty](https://scholarworks.brandeis.edu/esploro/outputs/translation/Local-Financial-Administration-in-the-Latter/9924144123301921), 2018, abstract.

Zhang Yibing describes early Song Three Bureaus fiscal planning and a later shift toward specified circuit contributions and greater Tax Transport Bureau autonomy after central processing became overloaded. This offers historical support for common fiscal authority with distributed execution. See [Evolution of the Three Bureaus' Fiscal Planning System in the Early Northern Song Dynasty](https://academic.hep.com.cn/fhc/EN/Y2024/V19/I2/181), 2024, abstract.

### Control of finances changed within a dynasty

The Song reorganization of 1082 changed relationships between the central departments and ministries. A permanently identical nine-department hierarchy should be treated as CK3's institutional abstraction. See [Sung government and politics, The Cambridge History of China](https://www.cambridge.org/core/books/cambridge-history-of-china/sung-government-and-politics/B360D3EB6D72ADEE74E46FD8570548EC).

Hartwell documents several Song treasuries and changes in the balance of fiscal authority. His discussion of the Yuanfeng Treasury describes disbursement requiring emperor and Chief Minister approval, and his treatment of the 1082 reorganization describes Revenue's relationship to the Council of State. This supplies an analogy for political oversight and reserved expenditure, not proof that every ministry shared that treasury. See [The Imperial Treasuries: Finance and Power in Song China](https://www.songyuan.org/JSYS/Archive/20/BSYS20_02_Hartwell.pdf), 1988, especially printed pp. 70-71.

The same study discusses palace reserves, state finances and debates over grants and loans between them. In this mod, CK3's imperial treasury remains a public account. It should not automatically be renamed the emperor's private purse; CK3 already has personal gold.

An early Tang budget study documents expenditure reports, imperial authorization and implementation by fiscal offices, while also explaining that the detailed annual system was replaced in 736. Use this as evidence of institutional diversity, not as an unchanged procedure for an 867 start. See Tohru Ohtsu, [On the National Budget under the Code-Statute Regime of the Tang Dynasty](https://www.jstage.jst.go.jp/article/shigaku/95/12/95_KJ00003673835/_article/-char/en), 1986, abstract.

## Candidates to compare

These are game-design interpretations. None is a claim to reproduce Tang/Song finance exactly.

| Candidate | Money custody and execution | Gameplay opportunity | Technical limitation |
|---|---|---|---|
| **Common fund in Revenue custody** | Revenue's native public treasury represents the ministerial exchequer. Operating advances cover other offices' native expenses. Imperial treasury remains separate. | Strong fiscal allocator; ministries compete for one funded programme. | Requires reliable expense timing, advances, native affordability and common-fund presentation. Full automatic account sharing remains unconfirmed. |
| **Common fund under Chancellor custody** | Chancellor's treasury holds the ministerial fund; Revenue administers authorized disbursements. | Creates a strong executive and potential conflict over release of funds. | Moving the custodian does not solve automatic native expense routing. Revenue's powers need protection or Chancellor becomes the effective finance minister. Historical support concerns some council-controlled funds, not a universal arrangement. |
| **Dedicated exchequer custodian** | An institutional treasury title/keeper holds the common fund, separate from all nine political ministries. | Separates custody, authorization and execution clearly. | An additional title, treasury eligibility, holder, succession, AI and UI all require an engine prototype. It adds administration and still needs expense routing. This is unproven, not a confirmed engine feature. |
| **Unified fiscal plan with assigned revenues** | Existing accounts remain. Revenue allocates authorized remittances and grants to meet approved commitments; ministries do not receive unrestricted fiscal independence. | Gives governors, Revenue and Chancellor recurring bargaining over actual obligations and funding. | This supplies coordinated finance rather than one physical bank balance. Direct rerouting of native taxes is unproven; using additional treasury transfers must avoid double charging. |

The last candidate is a serious comparison because it may achieve the desired political gameplay with fewer engine changes. It does not fully meet the preference for one physical ministerial balance. Keep that tradeoff explicit.

## Adaptable institutional framework

Compare three independent questions:

1. **Authority:** what can Revenue authorize, what needs Chancellor consent, and what remains reserved to the emperor?
2. **Custody:** who holds actual funds, and which reserves are protected?
3. **Execution:** how do approved wages, army maintenance and project expenses reach the native payer?

Adapt through reforms, standing mandates and the degree of central control. Tang and Song starts may use historically inspired defaults, while the player can change institutions. Avoid an automatic calendar switch that rewrites the player's government. Greater centralization should have administrative and political costs as well as benefits; it should not be an inevitable upgrade.

Routine authorized salaries and existing army commitments should proceed automatically. Major changes and disputed priorities should create decisions. Common planning does not require monthly salary popups or restoration of the removed review/register loops.

## Decision criteria and next investigation

- Historical institutional plausibility in both eras, with the game abstraction stated honestly.
- A consequential Revenue role and Chancellor oversight without making every official's routine action an approval event.
- Treasury conservation, separate imperial/personal/provincial accounts and protected military commitments.
- Native court hiring, army maintenance and project affordability continue functioning.
- Low popup volume, natural correspondence and clear effect previews.
- Small isolated module; existing Personnel appointment/service gameplay remains intact.

No final architecture should be chosen from historical analogy alone. Compare an operating-advance prototype with an assigned-remittance prototype, then measure money movement, native AI behavior, succession safety and player decisions. A dedicated custodian requires a separate title/treasury eligibility proof before it deserves preference over an existing office account.

This comparison has not changed gameplay files or replaced the current dev.48 implementation.
