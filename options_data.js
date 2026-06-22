window.OPTIONS_DATA = {
  "generated_at": "2026-06-22 05:24 UTC",
  "source": "DEMO(合成數據)",
  "config": {
    "min_dte": 30,
    "max_dte": 60,
    "min_oi": 500,
    "min_vol": 50,
    "max_spread_pct": 0.06,
    "buy_delta": [
      0.55,
      0.7
    ],
    "sell_delta": [
      0.15,
      0.3
    ]
  },
  "results": [
    {
      "ticker": "AAPL",
      "spot": 195.0,
      "atr": 5.09,
      "hv20": 0.2337,
      "hv_rank": 38.0,
      "atm_iv": 0.22,
      "iv_hv": 0.94,
      "earnings": "2026-07-10",
      "side": "BUY",
      "picks": [
        {
          "type": "CALL",
          "strike": 190.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 79.9,
          "mid": 8.64,
          "iv": 0.2203,
          "delta": 0.684,
          "gamma": 0.0268,
          "theta": -0.083,
          "vega": 0.215,
          "oi": 2857,
          "volume": 833,
          "spread_pct": 0.028,
          "reasons": [
            "流動性 25/25 (OI=2857,spr=2.8%)",
            "Delta 0.68 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=5.00, 1SD(IV)=13.28, ATR移動=21.51)",
            "IV regime 13/25 (IV/HV=0.94)",
            "⚠️ 到期前有earnings(2026-07-10),IV crush風險 -8"
          ]
        },
        {
          "type": "PUT",
          "strike": 200.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 79.9,
          "mid": 7.68,
          "iv": 0.2203,
          "delta": -0.608,
          "gamma": 0.0289,
          "theta": -0.057,
          "vega": 0.232,
          "oi": 3024,
          "volume": 886,
          "spread_pct": 0.031,
          "reasons": [
            "流動性 25/25 (OI=3024,spr=3.1%)",
            "Delta 0.61 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=5.00, 1SD(IV)=13.28, ATR移動=21.51)",
            "IV regime 13/25 (IV/HV=0.94)",
            "⚠️ 到期前有earnings(2026-07-10),IV crush風險 -8"
          ]
        },
        {
          "type": "CALL",
          "strike": 190.0,
          "expiry": "2026-08-06",
          "dte": 45,
          "score": 79.9,
          "mid": 9.43,
          "iv": 0.2203,
          "delta": 0.672,
          "gamma": 0.0239,
          "theta": -0.076,
          "vega": 0.247,
          "oi": 3206,
          "volume": 780,
          "spread_pct": 0.015,
          "reasons": [
            "流動性 25/25 (OI=3206,spr=1.5%)",
            "Delta 0.67 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=5.00, 1SD(IV)=15.06, ATR移動=24.39)",
            "IV regime 13/25 (IV/HV=0.94)",
            "⚠️ 到期前有earnings(2026-07-10),IV crush風險 -8"
          ]
        },
        {
          "type": "PUT",
          "strike": 200.0,
          "expiry": "2026-08-06",
          "dte": 45,
          "score": 79.9,
          "mid": 8.22,
          "iv": 0.2203,
          "delta": -0.586,
          "gamma": 0.0258,
          "theta": -0.05,
          "vega": 0.267,
          "oi": 3062,
          "volume": 792,
          "spread_pct": 0.034,
          "reasons": [
            "流動性 25/25 (OI=3062,spr=3.4%)",
            "Delta 0.59 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=5.00, 1SD(IV)=15.06, ATR移動=24.39)",
            "IV regime 13/25 (IV/HV=0.94)",
            "⚠️ 到期前有earnings(2026-07-10),IV crush風險 -8"
          ]
        },
        {
          "type": "CALL",
          "strike": 190.0,
          "expiry": "2026-08-19",
          "dte": 58,
          "score": 79.9,
          "mid": 10.37,
          "iv": 0.2203,
          "delta": 0.663,
          "gamma": 0.0213,
          "theta": -0.069,
          "vega": 0.284,
          "oi": 2896,
          "volume": 873,
          "spread_pct": 0.018,
          "reasons": [
            "流動性 25/25 (OI=2896,spr=1.8%)",
            "Delta 0.66 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=5.00, 1SD(IV)=17.10, ATR移動=27.69)",
            "IV regime 13/25 (IV/HV=0.94)",
            "⚠️ 到期前有earnings(2026-07-10),IV crush風險 -8"
          ]
        }
      ],
      "spreads": [
        {
          "name": "Bull Call Spread",
          "view": "溫和看升",
          "kind": "debit",
          "legs": [
            {
              "action": "BUY",
              "type": "CALL",
              "strike": 195.0,
              "mid": 6.54,
              "delta": 0.54
            },
            {
              "action": "SELL",
              "type": "CALL",
              "strike": 205.0,
              "mid": 2.72,
              "delta": 0.3
            }
          ],
          "net": 3.82,
          "width": 10.0,
          "max_profit": 6.18,
          "max_loss": 3.82,
          "rr": 1.62,
          "breakevens": [
            198.82
          ],
          "expiry": "2026-08-06",
          "dte": 45
        },
        {
          "name": "Bear Put Spread",
          "view": "溫和看跌",
          "kind": "debit",
          "legs": [
            {
              "action": "BUY",
              "type": "PUT",
              "strike": 200.0,
              "mid": 8.22,
              "delta": -0.59
            },
            {
              "action": "SELL",
              "type": "PUT",
              "strike": 190.0,
              "mid": 3.51,
              "delta": -0.33
            }
          ],
          "net": 4.71,
          "width": 10.0,
          "max_profit": 5.29,
          "max_loss": 4.71,
          "rr": 1.12,
          "breakevens": [
            195.29
          ],
          "expiry": "2026-08-06",
          "dte": 45
        }
      ]
    },
    {
      "ticker": "NVDA",
      "spot": 120.0,
      "atr": 6.65,
      "hv20": 0.5439,
      "hv_rank": 59.0,
      "atm_iv": 0.72,
      "iv_hv": 1.32,
      "earnings": "2026-07-01",
      "side": "SELL",
      "picks": [
        {
          "type": "PUT",
          "strike": 111.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 70.8,
          "mid": 6.48,
          "iv": 0.7435,
          "delta": -0.318,
          "gamma": 0.0129,
          "theta": -0.135,
          "vega": 0.133,
          "oi": 1948,
          "volume": 520,
          "spread_pct": 0.02,
          "reasons": [
            "流動性 23/25 (OI=1948,spr=2.0%)",
            "Delta 0.32 → 23/25 (目標0.15-0.3)",
            "到價配合 8/25 (距strike=9.00, 1SD(IV)=26.75, ATR移動=28.09)",
            "IV regime 16/25 (IV/HV=1.32)"
          ]
        },
        {
          "type": "PUT",
          "strike": 111.0,
          "expiry": "2026-08-06",
          "dte": 45,
          "score": 69.5,
          "mid": 7.76,
          "iv": 0.7435,
          "delta": -0.326,
          "gamma": 0.0115,
          "theta": -0.12,
          "vega": 0.152,
          "oi": 1950,
          "volume": 538,
          "spread_pct": 0.018,
          "reasons": [
            "流動性 24/25 (OI=1950,spr=1.8%)",
            "Delta 0.33 → 22/25 (目標0.15-0.3)",
            "到價配合 7/25 (距strike=9.00, 1SD(IV)=30.34, ATR移動=31.86)",
            "IV regime 16/25 (IV/HV=1.32)"
          ]
        },
        {
          "type": "PUT",
          "strike": 108.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 68.2,
          "mid": 5.5,
          "iv": 0.7555,
          "delta": -0.279,
          "gamma": 0.012,
          "theta": -0.13,
          "vega": 0.125,
          "oi": 1252,
          "volume": 426,
          "spread_pct": 0.036,
          "reasons": [
            "流動性 16/25 (OI=1252,spr=3.6%)",
            "Delta 0.28 → 25/25 (目標0.15-0.3)",
            "到價配合 11/25 (距strike=12.00, 1SD(IV)=26.75, ATR移動=28.09)",
            "IV regime 16/25 (IV/HV=1.32)"
          ]
        },
        {
          "type": "CALL",
          "strike": 141.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 68.2,
          "mid": 4.52,
          "iv": 0.7537,
          "delta": 0.289,
          "gamma": 0.0122,
          "theta": -0.14,
          "vega": 0.127,
          "oi": 526,
          "volume": 113,
          "spread_pct": 0.029,
          "reasons": [
            "流動性 8/25 (OI=526,spr=2.9%)",
            "Delta 0.29 → 25/25 (目標0.15-0.3)",
            "到價配合 19/25 (距strike=21.00, 1SD(IV)=26.75, ATR移動=28.09)",
            "IV regime 16/25 (IV/HV=1.32)"
          ]
        },
        {
          "type": "PUT",
          "strike": 111.0,
          "expiry": "2026-08-19",
          "dte": 58,
          "score": 67.2,
          "mid": 9.21,
          "iv": 0.7435,
          "delta": -0.332,
          "gamma": 0.0102,
          "theta": -0.105,
          "vega": 0.174,
          "oi": 2060,
          "volume": 475,
          "spread_pct": 0.025,
          "reasons": [
            "流動性 23/25 (OI=2060,spr=2.5%)",
            "Delta 0.33 → 22/25 (目標0.15-0.3)",
            "到價配合 6/25 (距strike=9.00, 1SD(IV)=34.44, ATR移動=36.16)",
            "IV regime 16/25 (IV/HV=1.32)"
          ]
        }
      ],
      "spreads": [
        {
          "name": "Bull Put Spread",
          "view": "看唔跌(收租)",
          "kind": "credit",
          "legs": [
            {
              "action": "BUY",
              "type": "PUT",
              "strike": 87.0,
              "mid": 2.64,
              "delta": -0.12
            },
            {
              "action": "SELL",
              "type": "PUT",
              "strike": 105.0,
              "mid": 5.83,
              "delta": -0.26
            }
          ],
          "net": 3.19,
          "width": 18.0,
          "max_profit": 3.19,
          "max_loss": 14.81,
          "rr": 0.21,
          "breakevens": [
            101.81
          ],
          "expiry": "2026-08-06",
          "dte": 45
        },
        {
          "name": "Bear Call Spread",
          "view": "看唔升(收租)",
          "kind": "credit",
          "legs": [
            {
              "action": "BUY",
              "type": "CALL",
              "strike": 165.0,
              "mid": 3.17,
              "delta": 0.18
            },
            {
              "action": "SELL",
              "type": "CALL",
              "strike": 150.0,
              "mid": 4.48,
              "delta": 0.26
            }
          ],
          "net": 1.31,
          "width": 15.0,
          "max_profit": 1.31,
          "max_loss": 13.69,
          "rr": 0.1,
          "breakevens": [
            151.31
          ],
          "expiry": "2026-08-06",
          "dte": 45
        },
        {
          "name": "Iron Condor",
          "view": "預期橫行(中性收租)",
          "kind": "credit",
          "legs": [
            {
              "action": "BUY",
              "type": "PUT",
              "strike": 87.0,
              "mid": 2.64,
              "delta": -0.12
            },
            {
              "action": "SELL",
              "type": "PUT",
              "strike": 105.0,
              "mid": 5.83,
              "delta": -0.26
            },
            {
              "action": "BUY",
              "type": "CALL",
              "strike": 165.0,
              "mid": 3.17,
              "delta": 0.18
            },
            {
              "action": "SELL",
              "type": "CALL",
              "strike": 150.0,
              "mid": 4.48,
              "delta": 0.26
            }
          ],
          "net": 4.5,
          "width": 18.0,
          "max_profit": 4.5,
          "max_loss": 13.5,
          "rr": 0.33,
          "breakevens": [
            100.5,
            154.5
          ],
          "expiry": "2026-08-06",
          "dte": 45
        }
      ]
    },
    {
      "ticker": "KO",
      "spot": 62.0,
      "atr": 0.88,
      "hv20": 0.1427,
      "hv_rank": 67.0,
      "atm_iv": 0.16,
      "iv_hv": 1.12,
      "earnings": null,
      "side": "SELL",
      "picks": [
        {
          "type": "CALL",
          "strike": 66.0,
          "expiry": "2026-08-06",
          "dte": 45,
          "score": 81.1,
          "mid": 0.29,
          "iv": 0.1611,
          "delta": 0.164,
          "gamma": 0.0705,
          "theta": -0.011,
          "vega": 0.054,
          "oi": 2306,
          "volume": 673,
          "spread_pct": 0.034,
          "reasons": [
            "流動性 25/25 (OI=2306,spr=3.4%)",
            "Delta 0.16 → 25/25 (目標0.15-0.3)",
            "到價配合 25/25 (距strike=4.00, 1SD(IV)=3.48, ATR移動=4.21)",
            "IV regime 6/25 (IV/HV=1.12)"
          ]
        },
        {
          "type": "CALL",
          "strike": 66.0,
          "expiry": "2026-08-19",
          "dte": 58,
          "score": 81.1,
          "mid": 0.44,
          "iv": 0.1611,
          "delta": 0.203,
          "gamma": 0.071,
          "theta": -0.011,
          "vega": 0.07,
          "oi": 2362,
          "volume": 605,
          "spread_pct": 0.045,
          "reasons": [
            "流動性 25/25 (OI=2362,spr=4.5%)",
            "Delta 0.20 → 25/25 (目標0.15-0.3)",
            "到價配合 25/25 (距strike=4.00, 1SD(IV)=3.95, ATR移動=4.78)",
            "IV regime 6/25 (IV/HV=1.12)"
          ]
        },
        {
          "type": "PUT",
          "strike": 58.0,
          "expiry": "2026-08-19",
          "dte": 58,
          "score": 79.7,
          "mid": 0.31,
          "iv": 0.1746,
          "delta": -0.137,
          "gamma": 0.0507,
          "theta": -0.007,
          "vega": 0.054,
          "oi": 2192,
          "volume": 610,
          "spread_pct": 0.0,
          "reasons": [
            "流動性 25/25 (OI=2192,spr=0.0%)",
            "Delta 0.14 → 24/25 (目標0.15-0.3)",
            "到價配合 25/25 (距strike=4.00, 1SD(IV)=3.95, ATR移動=4.78)",
            "IV regime 6/25 (IV/HV=1.12)"
          ]
        },
        {
          "type": "CALL",
          "strike": 66.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 78.7,
          "mid": 0.19,
          "iv": 0.1611,
          "delta": 0.127,
          "gamma": 0.0672,
          "theta": -0.01,
          "vega": 0.04,
          "oi": 2346,
          "volume": 671,
          "spread_pct": 0.0,
          "reasons": [
            "流動性 25/25 (OI=2346,spr=0.0%)",
            "Delta 0.13 → 23/25 (目標0.15-0.3)",
            "到價配合 25/25 (距strike=4.00, 1SD(IV)=3.07, ATR移動=3.72)",
            "IV regime 6/25 (IV/HV=1.12)"
          ]
        },
        {
          "type": "PUT",
          "strike": 58.0,
          "expiry": "2026-08-06",
          "dte": 45,
          "score": 76.4,
          "mid": 0.21,
          "iv": 0.1746,
          "delta": -0.113,
          "gamma": 0.0505,
          "theta": -0.007,
          "vega": 0.042,
          "oi": 2020,
          "volume": 672,
          "spread_pct": 0.047,
          "reasons": [
            "流動性 24/25 (OI=2020,spr=4.7%)",
            "Delta 0.11 → 21/25 (目標0.15-0.3)",
            "到價配合 25/25 (距strike=4.00, 1SD(IV)=3.48, ATR移動=4.21)",
            "IV regime 6/25 (IV/HV=1.12)"
          ]
        }
      ],
      "spreads": [
        {
          "name": "Bull Put Spread",
          "view": "看唔跌(收租)",
          "kind": "credit",
          "legs": [
            {
              "action": "BUY",
              "type": "PUT",
              "strike": 58.0,
              "mid": 0.21,
              "delta": -0.11
            },
            {
              "action": "SELL",
              "type": "PUT",
              "strike": 60.0,
              "mid": 0.55,
              "delta": -0.25
            }
          ],
          "net": 0.34,
          "width": 2.0,
          "max_profit": 0.34,
          "max_loss": 1.67,
          "rr": 0.2,
          "breakevens": [
            59.66
          ],
          "expiry": "2026-08-06",
          "dte": 45
        },
        {
          "name": "Bear Call Spread",
          "view": "看唔升(收租)",
          "kind": "credit",
          "legs": [
            {
              "action": "BUY",
              "type": "CALL",
              "strike": 66.0,
              "mid": 0.29,
              "delta": 0.16
            },
            {
              "action": "SELL",
              "type": "CALL",
              "strike": 64.0,
              "mid": 0.73,
              "delta": 0.33
            }
          ],
          "net": 0.44,
          "width": 2.0,
          "max_profit": 0.44,
          "max_loss": 1.56,
          "rr": 0.28,
          "breakevens": [
            64.44
          ],
          "expiry": "2026-08-06",
          "dte": 45
        },
        {
          "name": "Iron Condor",
          "view": "預期橫行(中性收租)",
          "kind": "credit",
          "legs": [
            {
              "action": "BUY",
              "type": "PUT",
              "strike": 58.0,
              "mid": 0.21,
              "delta": -0.11
            },
            {
              "action": "SELL",
              "type": "PUT",
              "strike": 60.0,
              "mid": 0.55,
              "delta": -0.25
            },
            {
              "action": "BUY",
              "type": "CALL",
              "strike": 66.0,
              "mid": 0.29,
              "delta": 0.16
            },
            {
              "action": "SELL",
              "type": "CALL",
              "strike": 64.0,
              "mid": 0.73,
              "delta": 0.33
            }
          ],
          "net": 0.78,
          "width": 2.0,
          "max_profit": 0.78,
          "max_loss": 1.22,
          "rr": 0.64,
          "breakevens": [
            59.22,
            64.78
          ],
          "expiry": "2026-08-06",
          "dte": 45
        }
      ]
    },
    {
      "ticker": "SPY",
      "spot": 540.0,
      "atr": 6.8,
      "hv20": 0.1569,
      "hv_rank": 73.0,
      "atm_iv": 0.12,
      "iv_hv": 0.76,
      "earnings": null,
      "side": "BUY",
      "picks": [
        {
          "type": "PUT",
          "strike": 546.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 96.8,
          "mid": 9.99,
          "iv": 0.12,
          "delta": -0.565,
          "gamma": 0.0196,
          "theta": -0.074,
          "vega": 0.658,
          "oi": 3189,
          "volume": 936,
          "spread_pct": 0.024,
          "reasons": [
            "流動性 25/25 (OI=3189,spr=2.4%)",
            "Delta 0.56 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=6.00, 1SD(IV)=20.07, ATR移動=28.72)",
            "IV regime 22/25 (IV/HV=0.76)"
          ]
        },
        {
          "type": "CALL",
          "strike": 532.0,
          "expiry": "2026-08-06",
          "dte": 45,
          "score": 96.8,
          "mid": 15.5,
          "iv": 0.12,
          "delta": 0.694,
          "gamma": 0.0154,
          "theta": -0.133,
          "vega": 0.665,
          "oi": 3332,
          "volume": 814,
          "spread_pct": 0.015,
          "reasons": [
            "流動性 25/25 (OI=3332,spr=1.5%)",
            "Delta 0.69 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=8.00, 1SD(IV)=22.75, ATR移動=32.57)",
            "IV regime 22/25 (IV/HV=0.76)"
          ]
        },
        {
          "type": "CALL",
          "strike": 532.0,
          "expiry": "2026-08-19",
          "dte": 58,
          "score": 96.8,
          "mid": 17.16,
          "iv": 0.12,
          "delta": 0.686,
          "gamma": 0.0137,
          "theta": -0.123,
          "vega": 0.763,
          "oi": 3022,
          "volume": 906,
          "spread_pct": 0.019,
          "reasons": [
            "流動性 25/25 (OI=3022,spr=1.9%)",
            "Delta 0.69 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=8.00, 1SD(IV)=25.83, ATR移動=36.97)",
            "IV regime 22/25 (IV/HV=0.76)"
          ]
        },
        {
          "type": "CALL",
          "strike": 532.0,
          "expiry": "2026-07-27",
          "dte": 35,
          "score": 96.4,
          "mid": 14.12,
          "iv": 0.12,
          "delta": 0.704,
          "gamma": 0.0172,
          "theta": -0.144,
          "vega": 0.578,
          "oi": 2983,
          "volume": 867,
          "spread_pct": 0.028,
          "reasons": [
            "流動性 25/25 (OI=2983,spr=2.8%)",
            "Delta 0.70 → 25/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=8.00, 1SD(IV)=20.07, ATR移動=28.72)",
            "IV regime 22/25 (IV/HV=0.76)"
          ]
        },
        {
          "type": "PUT",
          "strike": 546.0,
          "expiry": "2026-08-06",
          "dte": 45,
          "score": 96.1,
          "mid": 10.67,
          "iv": 0.12,
          "delta": -0.544,
          "gamma": 0.0174,
          "theta": -0.063,
          "vega": 0.752,
          "oi": 3260,
          "volume": 919,
          "spread_pct": 0.024,
          "reasons": [
            "流動性 25/25 (OI=3260,spr=2.4%)",
            "Delta 0.54 → 24/25 (目標0.55-0.7)",
            "到價配合 25/25 (距strike=6.00, 1SD(IV)=22.75, ATR移動=32.57)",
            "IV regime 22/25 (IV/HV=0.76)"
          ]
        }
      ],
      "spreads": [
        {
          "name": "Bull Call Spread",
          "view": "溫和看升",
          "kind": "debit",
          "legs": [
            {
              "action": "BUY",
              "type": "CALL",
              "strike": 532.0,
              "mid": 15.5,
              "delta": 0.69
            },
            {
              "action": "SELL",
              "type": "CALL",
              "strike": 560.0,
              "mid": 3.15,
              "delta": 0.24
            }
          ],
          "net": 12.36,
          "width": 28.0,
          "max_profit": 15.64,
          "max_loss": 12.36,
          "rr": 1.27,
          "breakevens": [
            544.36
          ],
          "expiry": "2026-08-06",
          "dte": 45
        },
        {
          "name": "Bear Put Spread",
          "view": "溫和看跌",
          "kind": "debit",
          "legs": [
            {
              "action": "BUY",
              "type": "PUT",
              "strike": 546.0,
              "mid": 10.67,
              "delta": -0.54
            },
            {
              "action": "SELL",
              "type": "PUT",
              "strike": 532.0,
              "mid": 4.75,
              "delta": -0.31
            }
          ],
          "net": 5.92,
          "width": 14.0,
          "max_profit": 8.09,
          "max_loss": 5.92,
          "rr": 1.37,
          "breakevens": [
            540.09
          ],
          "expiry": "2026-08-06",
          "dte": 45
        }
      ]
    }
  ]
};
