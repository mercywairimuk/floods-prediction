from django.db import models

class Farmer(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    soil_type = models.CharField(max_length=50)
    growth_stage = models.CharField(max_length=50)

    # ✅ Add these fields if your model expects them
    farm_size = models.FloatField(help_text="Farm size in acres")
    elevation = models.FloatField(default=100, help_text="Elevation in meters")

    def soil_type_index(self):
        """
        Converts soil_type to a numeric index for ML input.
        Update this mapping based on your training data.
        """
        soil_mapping = {
            'clay': 0,
            'sandy': 1,
            'loamy': 2,
            'silty': 3,
            'peaty': 4,
            'chalky': 5,
            'saline': 6
        }
        return soil_mapping.get(self.soil_type.lower(), -1)  # default to -1 if unknown

class FloodRisk(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    risk_level = models.CharField(max_length=50)
    yield_loss_estimate = models.FloatField()
    recommendation = models.TextField()
    date_predicted = models.DateTimeField(auto_now_add=True)

