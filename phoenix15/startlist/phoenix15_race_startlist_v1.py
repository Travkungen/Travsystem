import pandas as pd

class PhoenixRaceStartlist:
    VERSION = "1.0"
    STANDARD_COLUMNS = [
        "race_id","race_number","track_id","track_name","sport","country_code",
        "start_time","start_number","horse_id","horse_name","driver_id","driver_name",
        "trainer_id","trainer_name",
    ]

    def normalize(self, race, track=None):
        track = track or {}
        if not isinstance(race, dict):
            raise TypeError("race måste vara dict")
        starts = race.get("starts") or race.get("starters") or race.get("participants") or []
        rows = []
        for i, start in enumerate(starts, 1):
            if not isinstance(start, dict):
                continue
            horse = start.get("horse") or {}
            driver = start.get("driver") or start.get("jockey") or {}
            trainer = start.get("trainer") or {}
            rows.append({
                "race_id": race.get("id"),
                "race_number": race.get("number"),
                "track_id": track.get("id"),
                "track_name": track.get("name"),
                "sport": track.get("sport"),
                "country_code": track.get("countryCode"),
                "start_time": race.get("startTime"),
                "start_number": start.get("number") or start.get("startNumber") or start.get("postPosition") or i,
                "horse_id": start.get("horseId") or horse.get("id"),
                "horse_name": start.get("horseName") or horse.get("name"),
                "driver_id": start.get("driverId") or driver.get("id"),
                "driver_name": start.get("driverName") or driver.get("name"),
                "trainer_id": start.get("trainerId") or trainer.get("id"),
                "trainer_name": start.get("trainerName") or trainer.get("name"),
            })
        return pd.DataFrame(rows, columns=self.STANDARD_COLUMNS)

    def validate(self, df):
        required = ["race_id","race_number","horse_name","start_number"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise RuntimeError(f"Saknade obligatoriska kolumner: {missing}")
        return {
            "rows": len(df),
            "duplicates": int(df.duplicated(subset=["race_id","start_number"]).sum()),
            "missing_horse_names": int(df["horse_name"].isna().sum()),
        }
