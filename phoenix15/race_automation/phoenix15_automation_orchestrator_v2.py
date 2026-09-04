# ============================================================
# PHOENIX 15 — AUTOMATION ORCHESTRATOR v2
# ============================================================
# Adapter-based orchestration.
#
# Existing engines are NOT modified.
# Database write: False
# Model change: False
# ============================================================
from pathlib import Path
import importlib.util
import pandas as pd

class PhoenixAutomationOrchestratorV2:
    VERSION = "2.0"

    def __init__(
        self,
        auto_dir,
        model_path,
        conn=None,
    ):
        self.auto_dir = Path(auto_dir)
        self.model_path = Path(model_path)
        self.conn = conn
        self.discovery = None
        self.startlist = None
        self.history = None
        self.features = None
        self.model = None
        self.ranking = None
        self.top5 = None
        self.games = None

        # PHOENIX 15 — ODDS ENGINE
        odds_path = self.auto_dir.parent / "phoenix15" / "phoenix15_odds_engine_v1.py"
        spec = importlib.util.spec_from_file_location(
            "phoenix15_odds_engine_v1",
            odds_path
        )
        odds_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(odds_module)
        self.odds_engine = odds_module

    # --------------------------------------------------------
    # Dynamic module loader
    # --------------------------------------------------------
    def _load_class(self, filename, class_name):
        path = self.auto_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Motor saknas: {path}")
        spec = importlib.util.spec_from_file_location(
            f"phoenix15_auto_{class_name}",
            path,
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls = getattr(module, class_name)
        return cls

    # --------------------------------------------------------
    # Load engines
    # --------------------------------------------------------
    def load_engines(self):
        Discovery = self._load_class("phoenix15_race_discovery_v1.py", "PhoenixRaceDiscovery")
        Startlist = self._load_class("phoenix15_race_startlist_v1.py", "PhoenixRaceStartlist")
        History = self._load_class("phoenix15_horse_history_v1.py", "PhoenixHorseHistory")
        FeatureBuild = self._load_class("phoenix15_feature_build_v1.py", "PhoenixFeatureBuild")
        Model = self._load_class("phoenix15_model_engine_v1.py", "PhoenixModelEngine")
        Ranking = self._load_class("phoenix15_race_ranking_v1.py", "PhoenixRaceRanking")
        Top5 = self._load_class("phoenix15_top5_output_v1.py", "PhoenixTop5Output")
        GameDetection = self._load_class("phoenix15_game_detection_v1.py", "PhoenixGameDetection")
        self.discovery = Discovery()
        self.startlist = Startlist()
        if self.conn is None:
            raise RuntimeError("HorseHistory kräver en SQLite-connection.")
        self.history = History(self.conn)
        self.features = FeatureBuild()
        self.model = Model(self.model_path)
        self.ranking = Ranking()
        self.top5 = Top5()
        self.games = GameDetection()
        return True

    # --------------------------------------------------------
    # Game detection
    # --------------------------------------------------------
    def detect_games(self, today_data):
        result = self.games.summary(today_data)
        return result

    # --------------------------------------------------------
    # Discovery
    # --------------------------------------------------------
    def discover(self, today_data):
        return self.discovery.discover_from_today_data(today_data)

    # --------------------------------------------------------
    # Race object lookup
    # --------------------------------------------------------
    def _race_objects(self, today_data):
        objects = {}
        for track in today_data.get("tracks", []):
            for race in track.get("races", []):
                race_id = race.get("id")
                if race_id:
                    race_copy = dict(race)
                    race_copy["_track"] = track
                    objects[race_id] = race_copy
        return objects

    # --------------------------------------------------------
    # Startlist adapter
    # --------------------------------------------------------
    def build_startlist(self, today_data, discovered):
        ExtendedAdapter = self._load_class(
            "phoenix15_atg_extended_adapter_v2.py",
            "PhoenixATGExtendedAdapter",
        )
        extended_adapter = ExtendedAdapter()
        extended_races = extended_adapter.load_extended_races(today_data)
        frames = []
        for item in discovered:
            race_id = item.get("race_id")
            extended = extended_races.get(race_id)
            if extended is None:
                continue
            race = extended.get("race", {})
            track = extended.get("track", {})
            df = self.startlist.normalize(race, track=track)
            if df.empty:
                continue
            if "start_time" in df.columns:
                df["race_date"] = (
                    pd.to_datetime(df["start_time"], errors="coerce").dt.date.astype(str)
                )
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------
    def build_history(self, startlist):
        if startlist.empty:
            return pd.DataFrame()
        return self.history.build(startlist)

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------
    def build_features(self, startlist, history):
        df = self.features.build(startlist, horse_history=history)
        PersonBridge = self._load_class(
            "phoenix15_person_bridge_v1.py",
            "Phoenix15PersonBridge",
        )
        person_bridge = PersonBridge(self.conn)
        df = person_bridge.apply(df)
        self.features.validate(df)
        return df

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------
    def predict(self, feature_df):
        X = self.features.model_matrix(feature_df)
        prediction = self.model.predict(X)
        metadata = feature_df.reset_index(drop=True).copy()
        prediction = prediction.reset_index(drop=True)
        if len(metadata) != len(prediction):
            raise RuntimeError("Metadata och modellresultat har olika antal rader.")
        scored = metadata.copy()
        for col in ["win_probability", "model_rank"]:
            if col in prediction.columns:
                scored[col] = prediction[col].to_numpy()
        if "win_probability" not in scored.columns:
            raise RuntimeError("Modellen returnerade ingen win_probability.")
        return scored

    # --------------------------------------------------------
    # Ranking
    # --------------------------------------------------------
    def rank(self, scored):
        ranked = self.ranking.rank(scored)
        self.ranking.validate(ranked)
        self._save_prediction_snapshot(ranked)
        return ranked

    # --------------------------------------------------------
    # Prediction Snapshot
    # --------------------------------------------------------
    def _save_prediction_snapshot(self, ranked):
        from pathlib import Path
        from datetime import datetime
        import json
        phoenix_root = Path(__file__).resolve().parents[1]
        snapshot_root = phoenix_root / "snapshots" / "predictions"
        snapshot_root.mkdir(parents=True, exist_ok=True)
        race_col = None
        for c in ["atg_race_id", "race_id", "raceid"]:
            if c in ranked.columns:
                race_col = c
                break
        if race_col is None:
            raise RuntimeError("Kan inte skapa prediction snapshot: race-id saknas.")
        forbidden = {
            "result", "resultat", "finish", "finishing_position", "placement", "winner",
        }
        safe_columns = [c for c in ranked.columns if str(c).lower() not in forbidden]
        snapshot = {
            "snapshot_version": "phoenix15_prediction_snapshot_v1",
            "created_at": datetime.now().isoformat(),
            "source": "phoenix15_automation_orchestrator_v2",
            "races": {}
        }
        for race_id, group in ranked.groupby(race_col):
            group = group.sort_values("phoenix_rank", ascending=True)
            snapshot["races"][str(race_id)] = {
                "rows": group[safe_columns].to_dict(orient="records"),
                "row_count": len(group)
            }
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = snapshot_root / f"PREDICTION_SNAPSHOT_{timestamp}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2, default=str)
        return path

    # --------------------------------------------------------
    # Top 5
    # --------------------------------------------------------
    def build_top5(self, ranked):
        result = self.top5.build(ranked, n=5)
        self.top5.validate(result, n=5)
        return result

    # --------------------------------------------------------
    # Full pipeline
    # --------------------------------------------------------
    def run(self, today_data):
        if not isinstance(today_data, dict):
            raise TypeError("today_data måste vara dict")
        self.load_engines()
        games = self.detect_games(today_data)
        discovered = self.discover(today_data)
        startlist = self.build_startlist(today_data, discovered)
        if startlist.empty:
            raise RuntimeError("Ingen startlista kunde byggas.")
        startlist_validation = self.startlist.validate(startlist)
        history = self.build_history(startlist)
        features = self.build_features(startlist, history)
        scored = self.predict(features)
        ranked = self.rank(scored)
        # PHOENIX 15 — AUTOMATIC ODDS
        odds = self.odds_engine.fetch_market(discovered)
        top5 = self.build_top5(ranked)
        return {
            "games": games,
            "discovered": discovered,
            "startlist": startlist,
            "startlist_validation": startlist_validation,
            "history": history,
            "features": features,
            "scored": scored,
            "ranked": ranked,
            "odds": odds,
            "top5": top5,
        }
