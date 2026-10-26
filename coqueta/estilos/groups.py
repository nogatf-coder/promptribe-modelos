# El entorno de la foto, en grupos (dentro de cada grupo se elige una opción): lugar, momento, luz y plano
GROUPS = {
  "place": {
    "indoor": ["a photo taken indoors", "a photo inside a room or a building"],
    "outdoor": ["a photo taken outdoors", "a photo outside on the street or in nature"],
  },
  "time": {
    "day": ["a photo taken during the day in daylight"],
    "night": ["a photo taken at night", "a dark night scene with artificial lights"],
    "dusk": ["a photo taken at sunset or dusk", "golden hour light at sunset"],
  },
  "light": {
    "daylight": ["soft natural daylight", "a photo lit by natural window light"],
    "harshsun": ["harsh direct sunlight with hard shadows"],
    "overcast": ["overcast soft cloudy light"],
    "backlit": ["a backlit photo with the light behind the person"],
    "flash": ["a photo taken with direct camera flash", "harsh flash photography at night"],
    "led": ["colored led or neon light, purple, pink or blue light", "a room lit by colored led strips"],
    "warmlamp": ["warm indoor lamp light", "orange tungsten light indoors"],
    "dim": ["a dim photo in low light"],
  },
  "shot": {
    "closeup": ["a close-up portrait of a face"],
    "selfie": ["a selfie taken at arm's length"],
    "mirror": ["a mirror selfie holding a phone"],
    "halfbody": ["a half body portrait from the waist up"],
    "fullbody": ["a full body photo of a person standing"],
    "sitting": ["a person sitting or kneeling on the floor"],
    "group": ["a group of people"],
    "nobody": ["a photo with no people"],
  },
}
