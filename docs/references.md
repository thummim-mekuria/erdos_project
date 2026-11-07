# References

All sources accessed 6 November 2026 unless stated otherwise. Where a publication date could not
be confirmed it is marked "n.d."

## Price data

**[D1] Main price series — WFP market monitoring (via HDX)**
World Food Programme. (2026). *Kenya – Food Prices* [Data set; resource `wfp_food_prices_ken.csv`].
Humanitarian Data Exchange (HDX), UN OCHA. Dataset ID e0d3fba6-f9a2-45d7-b949-140c455197ff;
temporal coverage 15 January 2006 – 15 October 2026; last modified 4 November 2026.
<https://data.humdata.org/dataset/wfp-food-prices-for-kenya>. Licence: Creative Commons
Attribution for Intergovernmental Organisations (CC BY-IGO 3.0).
*Used:* market "Eldoret town (Uasin Gishu)", wholesale maize (per kg, and per 90-kg bag ÷ 90),
2006-01 → 2025-06. HDX lists the compiled sources as including Kenya's Ministry of Agriculture,
the Kenya National Bureau of Statistics (KNBS) and FAO's Food Price Monitoring and Analysis (FPMA).
Companion resource: *Kenya – Markets* (`wfp_markets_ken.csv`, last modified 18 February 2026).

**[D2] Gap-filling series and challenge data — Zindi / agriBORA**
Zindi & agriBORA. (2025–2026). *agriBORA Commodity Price Forecasting Challenge* [Competition data set].
Zindi. <https://zindi.africa/competitions/agribora-commodity-price-forecasting-challenge>.
Files: `kamis_maize_prices.csv` and `kamis_maize_prices_raw.csv` (created 12 November 2025),
`agriBORA_maize_prices.csv` (9 December 2025), `agriBORA_maize_prices_weeks_46_to_51.csv`
(23 December 2025), `agriBORA_Final_Weeks_maize_price.csv` (14 January 2026); archive generated
14 January 2026. Data provided by agriBORA; challenge partner Digital Africa. Terms: challenge
rules — "Data Sharing: Open source".
*Used:* KAMIS Eldoret Main Market, dry white maize, wholesale (monthly median) to fill five
months missing from [D1]; agriBORA prices used only for the price-level comparison.

**[D3] Original source of the KAMIS series**
Ministry of Agriculture, Republic of Kenya. (n.d.). *Kenya Agricultural Market Information System
(KAMIS)* [Online database]. <https://kamis.kilimo.go.ke>. Accessed through [D2]; the portal could
not be reached directly on 6 November 2026.

**[D4] Consulted, not used in the final analysis**
Kenya National Bureau of Statistics. (n.d.). *National average monthly wholesale prices 2012–2023
(source: KAMIS, Ministry of Agriculture)* [Data set]. National Information Platform for Food
Security and Nutrition. <https://nipfn.knbs.or.ke/download/national-average-monthly-wholesales-prices-2012-2023-source-kamis-ministry-of-agriculture/>.

## Cost inputs and context

**[S1] agriGHALA (storage, insurance, receipt-backed loans, harvest calendar, Q1 2026 results)**
Kenduiywo, B., Ngige, C. M., Kiogora, J., Alungwa, C., Ogolla, J., Odhiambo, K., & Schmidt, M.
(2026, May 12). *Enabling private-sector innovation in agricultural storage: Lessons from the
agriGHALA warehouse receipt model in Kenya* [Policy brief, 11 pp.]. International Center for
Tropical Agriculture (CIAT), agriBORA & P4G. <https://hdl.handle.net/10568/182900>

**[S2] On-farm storage losses**
De Groote, H., Muteti, F. N., & Bruce, A. Y. (2023). On-farm storage loss estimates of maize in
Kenya using community survey methods. *Journal of Stored Products Research, 102*, 102107.
<https://doi.org/10.1016/j.jspr.2023.102107>

**[S3] Interest rate (Central Bank of Kenya average commercial-bank lending rates, as reported)**
HapaKenya. (2025, July 2). *Kenya's average commercial bank lending rate dropped to 15.44% in May
2025.* <https://hapakenya.com/2025/07/02/kenyas-average-commercial-bank-lending-rate-dropped-to-15-44-in-may-2025>
Business Daily. (n.d.). *Banks lend Sh228bn new loans to businesses and households.*
<https://www.businessdailyafrica.com/bd/economy/banks-lend-sh228bn-new-loans-to-businesses-households-5368368>

**[S4] Warehouse storage fees (Warehouse Receipt System tariff, ≈ 2020)**
People Daily. (n.d.). *Warehouse receipt system opens stores to maize farmers.*
<https://peopledaily.digital/business/warehouse-receipt-system-opens-stores-to-maize-farmers>
The Standard. (n.d.). *Warehouses idle as Rift farmers opt to store their produce at home.*
<https://www.standardmedia.co.ke/counties/article/2001467107/warehouses-idle-as-rift-farmers-opt-to-store-their-produce-at-home>

**[S5] Harvest timing in Uasin-Gishu**
The New Humanitarian, via ReliefWeb. (n.d.). *Food crisis looms following low rainfall in maize
region.* <https://reliefweb.int/report/kenya/food-crisis-looms-following-low-rainfall-maize-region>
FAO Global Information and Early Warning System (GIEWS). (2026). *Country brief: Kenya.*
<https://cb.apps.fao.org/country.jsp?code=KEN>

**[S6] No exchange-traded maize futures in Kenya**
Capital Markets Authority (Kenya). (n.d.). *Derivatives* [Brochure].
<https://cma.or.ke/download/15/brochures/5491/derivatives-brochure.pdf>
The EastAfrican. (n.d.). *Kenya agricultural commodities exchange to go live in 2024.*
<https://www.theeastafrican.co.ke/tea/business/kenya-agricultural-commodities-exchange-to-go-live-in-2024-4433186>
Business Daily. (n.d.). *Kenya agricultural commodities exchange goes live next February.*
<https://www.businessdailyafrica.com/bd/economy/kenya-agricultural-commodities-exchange-goes-live-next-february--4432574>

**[S7] Agricultural Finance Corporation lending rate (≈ 10%)**
Business Daily. (n.d.). *AFC managing director George Kubai on unlocking access to credit for
Kenyan smallholder farmers.*
<https://www.businessdailyafrica.com/bd/corporate/boss-talk/afc-managing-director-george-kubai-on-unlocking-access-to-credit-for-kenyan-smallholder-farmer-5162832>

## Methods reference

Schwartz, E. S. (1997). The stochastic behavior of commodity prices: Implications for valuation and
hedging. *The Journal of Finance, 52*(3), 923–973. (Mean-reverting commodity price model, cited as a
possible extension.)
