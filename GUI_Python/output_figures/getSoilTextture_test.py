def SoilClassification(sand: float, silt: float) -> str:
    """
    Classify soil texture based on sand, silt, and clay percentages using USDA soil texture triangle.
    
    Parameters:
    - sand: Percentage of sand in the soil (0-100)
    - silt: Percentage of silt in the soil (0-100)
    - clay: Percentage of clay in the soil (0-100)
    
    Returns:
    - A string representing the soil texture class.
    """

clay= 100.0-sand-silt   # type: ignore # Note: the sum should be 100

if sand <= 45 and silt <= 40 and clay >= 40:
    texture = "Clay"
elif sand <= 65 and sand >= 45 and silt <= 20 and clay >= 35 and clay <= 55:
    texture = "Sandy Clay"
elif sand <= 20 and silt >= 40 and silt <= 60 and clay >= 40 and clay <= 60:
    texture = "Silty Clay"
elif sand >= 45 and sand <= 80 and silt <= 28 and clay >= 20 and clay <= 35:
    texture = "Sandy Clay Loam"
elif sand >= 20 and sand <= 45 and silt >= 15 and silt <= 53 and clay >= 27 and clay <= 40:
    texture = "Clay Loam"
elif sand <= 20 and silt >= 40 and silt <= 73 and clay >= 27 and clay <= 40:
    texture = "Silty Clay Loam"
elif sand >= 43 and sand <= 85 and silt <= 50 and clay <= 20:
    texture = "Sandy Loam"
elif sand >= 23 and sand <= 52 and silt >= 28 and silt <= 50 and clay >= 7 and clay <= 27:
    texture = "Loam"
elif sand <= 50 and silt >= 50 and silt <= 88 and clay <= 27:
    texture = "Silt Loam"
elif sand <= 20 and silt >= 80 and clay <= 12:
    texture = "Silt"
elif sand >= 70 and sand <= 90 and silt <= 30 and clay <= 15:
    texture = "Loamy Sand"
elif sand >= 85 and silt <= 15 and clay <= 10:
    texture = "Sand"
else:
    texture = "Not Available"
    
# print(f"For {sand}% Sand, {silt}% Silt, and {clay}% Clay:")
# print(f"The soil texture class is: {texture}")