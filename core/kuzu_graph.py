"""
Vigyan AI: Embedded C++ KùzuDB Knowledge Graph Engine
Indexes physical laws, semiconductor VLSI constants, and orbital astrodynamics axioms.
"""

import os
from typing import List, Dict, Any, Optional

class KuzuSTEMGraph:
    def __init__(self, db_path: str = "/tmp/vigyan_showcase_kuzu.db"):
        self.db_path = db_path
        self.kuzu_ready = False
        
        self.raw_laws = [
            ("Ohm's Law", "Circuits", "V = I * R", "Voltage across a conductor equals current multiplied by resistance."),
            ("Joule Heating Law", "Circuits", "P = I^2 * R = V^2 / R", "Power dissipated as heat in an electrical conductor."),
            ("Kirchhoff's Current Law", "Circuits", "sum(I_in) = sum(I_out)", "Conservation of charge at any electrical node."),
            ("Kirchhoff's Voltage Law", "Circuits", "sum(V_loop) = 0", "Conservation of electrical energy around any closed loop."),
            ("Faraday's Law of Induction", "Electromagnetism", "emf = - dPhi_B / dt", "Induced electromotive force equals negative time rate of magnetic flux change."),
            ("RC Time Constant", "Circuits", "tau = R * C", "Time required for capacitor to charge to ~63.2% of supply voltage."),
            ("MOSFET Saturation Current", "VLSI", "I_d = 0.5 * mu * C_ox * (W/L) * (V_gs - V_th)^2 * (1 + lambda * V_ds)", "Drain current in pinch-off saturation region with channel-length modulation."),
            ("Vis-Viva Law", "Astrodynamics", "v^2 = G * M * (2/r - 1/a)", "Equation governing the speed of an orbiting celestial body or satellite."),
            ("Kepler's Third Law", "Astrodynamics", "T^2 = (4 * pi^2 / (G * M)) * a^3", "Square of orbital period is proportional to cube of semi-major axis."),
            ("Tsiolkovsky Rocket Equation", "Aerospace", "Delta_v = I_sp * g_0 * ln(m_0 / m_f)", "Velocity change achieved by vehicle expelling reaction mass."),
            ("Carnot Limit", "Thermodynamics", "eta_max = 1 - (T_cold / T_hot)", "Upper theoretical limit for heat engine thermal efficiency."),
            ("First Law of Thermodynamics", "Thermodynamics", "Delta_U = Q - W", "Internal energy change equals heat added minus work done by system.")
        ]
        self.raw_concepts = [
            ("Capacitive Reactance", "Circuits", "Impedance offered by capacitor: Xc = 1/(omega * C)"),
            ("Cutoff Frequency", "Circuits", "Corner frequency where filter output drops 3dB: f_c = 1/(2*pi*R*C)"),
            ("Subthreshold Conduction", "VLSI", "Leakage current flowing through MOSFET channel when Vgs < Vth"),
            ("Velocity Saturation", "VLSI", "Carrier drift velocity saturates at critical lateral electric fields due to optical phonon scattering"),
            ("Escape Velocity", "Astrodynamics", "Minimum speed required to escape gravitational pull: v_esc = sqrt(2*G*M/R)"),
            ("Threshold Voltage Roll-Off", "VLSI", "Reduction in threshold voltage Vt as channel length shrinks due to DIBL and charge sharing")
        ]
        self.raw_constants = [
            ("Speed of Light", "c", "299792458", "m/s"),
            ("Planck Constant", "h", "6.62607015e-34", "J s"),
            ("Gravitational Constant", "G", "6.67430e-11", "N m^2 / kg^2"),
            ("Standard Gravity", "g0", "9.80665", "m/s^2"),
            ("Elementary Charge", "q", "1.602176634e-19", "C"),
            ("Boltzmann Constant", "k_B", "1.380649e-23", "J/K")
        ]

        try:
            import kuzu
            if os.path.exists(self.db_path):
                if os.path.isdir(self.db_path):
                    import shutil
                    shutil.rmtree(self.db_path)
                else:
                    os.remove(self.db_path)
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.db = kuzu.Database(self.db_path)
            self.conn = kuzu.Connection(self.db)
            self._seed_graph()
            self.kuzu_ready = True
        except Exception:
            self.kuzu_ready = False

    def _seed_graph(self):
        try:
            self.conn.execute("CREATE NODE TABLE Law(name STRING, domain STRING, equation STRING, description STRING, PRIMARY KEY (name))")
            self.conn.execute("CREATE NODE TABLE Concept(name STRING, field STRING, definition STRING, PRIMARY KEY (name))")
            self.conn.execute("CREATE NODE TABLE Constant(name STRING, symbol STRING, value STRING, units STRING, PRIMARY KEY (name))")
        except Exception:
            return

        for name, dom, eq, desc in self.raw_laws:
            self.conn.execute("CREATE (:Law {name: $n, domain: $d, equation: $e, description: $desc})",
                              {"n": name, "d": dom, "e": eq, "desc": desc})

        for name, fld, dfn in self.raw_concepts:
            self.conn.execute("CREATE (:Concept {name: $n, field: $f, definition: $d})", {"n": name, "f": fld, "d": dfn})

        for name, sym, val, u in self.raw_constants:
            self.conn.execute("CREATE (:Constant {name: $n, symbol: $s, value: $v, units: $u})",
                              {"n": name, "s": sym, "v": val, "u": u})

    def query_multihop_context(self, keywords: List[str]) -> str:
        matched = []
        if self.kuzu_ready:
            try:
                for kw in keywords:
                    kw_clean = kw.strip()
                    if len(kw_clean) < 3: continue
                    res = self.conn.execute("MATCH (l:Law) WHERE lower(l.name) CONTAINS lower($kw) OR lower(l.description) CONTAINS lower($kw) RETURN l.name, l.equation, l.description;", {"kw": kw_clean})
                    while res.has_next():
                        n, eq, d = res.get_next()
                        matched.append(f"- [Law]: {n} | Eq: {eq} | Axiom: {d}")
                    res_c = self.conn.execute("MATCH (c:Concept) WHERE lower(c.name) CONTAINS lower($kw) OR lower(c.definition) CONTAINS lower($kw) RETURN c.name, c.definition;", {"kw": kw_clean})
                    while res_c.has_next():
                        n, d = res_c.get_next()
                        matched.append(f"- [Concept]: {n} | Def: {d}")
                    res_k = self.conn.execute("MATCH (k:Constant) WHERE lower(k.name) CONTAINS lower($kw) OR lower(k.symbol) = lower($kw) RETURN k.name, k.symbol, k.value, k.units;", {"kw": kw_clean})
                    while res_k.has_next():
                        n, s, v, u = res_k.get_next()
                        matched.append(f"- [Constant]: {n} ({s}) = {v} {u}")
                if matched:
                    return "\n".join(matched[:5])
            except Exception:
                pass

        # In-Memory Fast Fallback
        for kw in keywords:
            kw_low = kw.strip().lower()
            if len(kw_low) < 3: continue
            for n, d, eq, desc in self.raw_laws:
                if kw_low in n.lower() or kw_low in desc.lower():
                    matched.append(f"- [Law]: {n} | Eq: {eq} | Axiom: {desc}")
            for n, fld, dfn in self.raw_concepts:
                if kw_low in n.lower() or kw_low in dfn.lower():
                    matched.append(f"- [Concept]: {n} | Def: {dfn}")
            for n, sym, val, u in self.raw_constants:
                if kw_low in n.lower() or kw_low == sym.lower():
                    matched.append(f"- [Constant]: {n} ({sym}) = {val} {u}")

        return "\n".join(matched[:5]) if matched else ""
