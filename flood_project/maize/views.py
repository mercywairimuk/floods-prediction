from django.shortcuts import render, redirect
from .forms import FarmerForm
from .models import Farmer, FloodRisk
import requests
import joblib
import datetime
import os
from django.conf import settings
from .forms import FarmerForm


from django.http import HttpResponse
from django.template.loader import render_to_string

def explanation(request, risk_id):
    risk = FloodRisk.objects.get(id=risk_id)
    summary = f"""
    Dear {risk.farmer.name},

    Based on your farm's data:
    - Location: {risk.farmer.location}
    - Soil Type: {risk.farmer.soil_type}
    - Farm Size: {risk.farmer.farm_size} acres
    - Elevation: {risk.farmer.elevation} meters

    The system predicts a flood risk level of **{risk.risk_level}**.
    Expected yield loss is approximately **{risk.yield_loss_estimate}%**.

    Recommendation: {risk.recommendation}
    """

    if request.GET.get('download') == '1':
        response = HttpResponse(summary, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename=prediction_summary_{risk.id}.txt'
        return response

    return render(request, 'maize/explanation.html', {'risk': risk, 'summary': summary})



# Load models once
risk_model_path = os.path.join(settings.BASE_DIR, 'maize', 'flood_risk_model.pkl')
yield_model_path = os.path.join(settings.BASE_DIR, 'maize', 'yield_loss_model.pkl')

flood_risk_model = joblib.load(risk_model_path)
yield_loss_model = joblib.load(yield_model_path)

from django import forms
from .models import Farmer

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required



CONSTITUENCY_COORDINATES= {
    '1. Changamwe': {'latitude': -4.0436, 'longitude': 39.6714},
    '2. Jomvu': {'latitude': -4.0412, 'longitude': 39.7064},
    '3. Kisauni': {'latitude': -4.0401, 'longitude': 39.7341},
    '4. Nyali': {'latitude': -4.0254, 'longitude': 39.7705},
    '5. Likoni': {'latitude': -4.1312, 'longitude': 39.6174},
    '6. Mvita': {'latitude': -4.0455, 'longitude': 39.6722},
    '7. Msambweni': {'latitude': -4.2303, 'longitude': 39.7101},
    '8. Lunga Lunga': {'latitude': -4.5667, 'longitude': 39.3847},
    '9. Matuga': {'latitude': -4.4532, 'longitude': 39.6293},
    '10. Kinango': {'latitude': -4.4519, 'longitude': 39.5685},
    '11. Kilifi North': {'latitude': -3.9129, 'longitude': 39.8574},
    '12. Kilifi South': {'latitude': -3.7986, 'longitude': 39.9608},
    '13. Kaloleni': {'latitude': -3.9898, 'longitude': 39.7511},
    '14. Rabai': {'latitude': -3.9333, 'longitude': 39.7500},
    '15. Ganze': {'latitude': -3.5795, 'longitude': 39.7397},
    '16. Malindi': {'latitude': -3.2216, 'longitude': 40.1226},
    '17. Magarini': {'latitude': -3.2068, 'longitude': 40.0349},
    '18. Garsen': {'latitude': -2.8580, 'longitude': 40.0473},
    '19. Galole': {'latitude': -2.8123, 'longitude': 40.1259},
    '20. Bura': {'latitude': -2.6563, 'longitude': 40.1111},
    '21. Lamu East': {'latitude': -2.2471, 'longitude': 40.8724},
    '22. Lamu West': {'latitude': -2.3209, 'longitude': 40.7367},
    '23. Taveta': {'latitude': -3.3903, 'longitude': 38.5895},
    '24. Wundanyi': {'latitude': -3.3124, 'longitude': 38.2794},
    '25. Mwatate': {'latitude': -3.4601, 'longitude': 38.3314},
    '26. Voi': {'latitude': -3.3965, 'longitude': 38.5623},
    '27. Garissa Township': {'latitude': -0.4590, 'longitude': 39.6547},
    '28. Balambala': {'latitude': -0.8654, 'longitude': 39.4671},
    '29. Lagdera': {'latitude': -0.7101, 'longitude': 39.5473},
    '30. Dadaab': {'latitude': -0.0346, 'longitude': 40.0333},
    '31. Fafi': {'latitude': -0.0537, 'longitude': 40.4391},
    '32. Ijara': {'latitude': -1.0702, 'longitude': 40.1822},
    '33. Wajir North': {'latitude': 1.9975, 'longitude': 40.0733},
    '34. Wajir East': {'latitude': 1.6750, 'longitude': 40.0849},
    '35. Tarbaj': {'latitude': 1.8462, 'longitude': 40.2562},
    '36. Wajir West': {'latitude': 1.6482, 'longitude': 39.7957},
    '37. Eldas': {'latitude': 1.8993, 'longitude': 39.7445},
    '38. Wajir South': {'latitude': 1.8171, 'longitude': 40.1133},
    '39. Mandera West': {'latitude': 3.1823, 'longitude': 41.8896},
    '40. Banissa': {'latitude': 3.4946, 'longitude': 41.7321},
    '41. Mandera North': {'latitude': 3.2068, 'longitude': 41.8129},
    '42. Mandera South': {'latitude': 2.7463, 'longitude': 41.7062},
    '43. Mandera East': {'latitude': 3.0734, 'longitude': 41.7348},
    '44. Lafey': {'latitude': 2.7349, 'longitude': 41.7322},
    '45. Moyale': {'latitude': 3.5249, 'longitude': 39.0714},
    '46. North Horr': {'latitude': 3.3836, 'longitude': 38.7039},
    '47. Saku': {'latitude': 0.0474, 'longitude': 37.8124},
    '48. Laisamis': {'latitude': 0.0851, 'longitude': 37.4171},
    '49. Isiolo North': {'latitude': 0.3975, 'longitude': 37.5858},
    '50. Isiolo South': {'latitude': 0.2662, 'longitude': 37.6943},
    '51. Igembe South': {'latitude': -0.2207, 'longitude': 37.9095},
    '52. Igembe Central': {'latitude': -0.2876, 'longitude': 37.7243},
    '53. Igembe North': {'latitude': -0.2861, 'longitude': 37.6192},
    '54. Tigania West': {'latitude': -0.1263, 'longitude': 37.8575},
    '55. Tigania East': {'latitude': -0.1394, 'longitude': 37.7672},
    '56. North Imenti': {'latitude': -0.0294, 'longitude': 37.6888},
    '57. Buuri': {'latitude': -0.0088, 'longitude': 37.5446},
    '58. Central Imenti': {'latitude': -0.0606, 'longitude': 37.7512},
    '59. South Imenti': {'latitude': -0.1344, 'longitude': 37.6256},
    '60. Maara': {'latitude': -0.4559, 'longitude': 37.6727},
    '61. Chuka/Igambangombe': {'latitude': -0.2954, 'longitude': 37.5686},
    '62. Tharaka': {'latitude': -0.2782, 'longitude': 37.6017},
    '63. Manyatta': {'latitude': -0.3071, 'longitude': 37.6869},
    '64. Runyenjes': {'latitude': -0.5376, 'longitude': 37.7021},
    '65. Mbeere South': {'latitude': -0.7863, 'longitude': 37.6778},
    '66. Mbeere North': {'latitude': -0.9193, 'longitude': 37.6297},
    '67. Mwingi North': {'latitude': -0.1067, 'longitude': 38.1697},
    '68. Mwingi West': {'latitude': -0.1721, 'longitude': 38.2425},
    '69. Mwingi Central': {'latitude': -0.2357, 'longitude': 38.2103},
    '70. Kitui West': {'latitude': -1.2042, 'longitude': 38.0735},
    '71. Kitui Rural': {'latitude': -1.3273, 'longitude': 38.0895},
    '72. Kitui Central': {'latitude': -1.3147, 'longitude': 38.0902},
    '73. Kitui East': {'latitude': -1.2631, 'longitude': 38.2078},
    '74. Kitui South': {'latitude': -1.3075, 'longitude': 38.3243},
    '75. Masinga': {'latitude': -1.5062, 'longitude': 37.5965},
    '76. Yatta': {'latitude': -1.5307, 'longitude': 37.6611},
    '77. Kangundo': {'latitude': -1.3982, 'longitude': 37.5368},
    '78. Matungulu': {'latitude': -1.3192, 'longitude': 37.7035},
    '79. Kathiani': {'latitude': -1.3072, 'longitude': 37.7099},
    '80. Mavoko': {'latitude': -1.3469, 'longitude': 37.2357},
    '81. Machakos Town': {'latitude': -1.5198, 'longitude': 37.2621},
    '82. Mwala': {'latitude': -1.4956, 'longitude': 37.5054},
    '83. Mbooni': {'latitude': -1.5297, 'longitude': 37.4997},
    '84. Kilome': {'latitude': -1.5363, 'longitude': 37.6076},
    '85. Kaiti': {'latitude': -1.5246, 'longitude': 37.6575},
    '86. Makueni': {'latitude': -1.7781, 'longitude': 37.6988},
    '87. Kibwezi West': {'latitude': -2.5026, 'longitude': 37.6571},
    '88. Kibwezi East': {'latitude': -2.4692, 'longitude': 37.6375},
    '89. Kinangop': {'latitude': -0.7519, 'longitude': 37.1992},
    '90. Kipipiri': {'latitude': -0.6956, 'longitude': 37.2417},
    '91. Ol Kalou': {'latitude': -0.5671, 'longitude': 37.2267},
    '92. Ol Jorok': {'latitude': -0.5524, 'longitude': 37.0971},
    '93. Ndaragwa': {'latitude': -0.6019, 'longitude': 37.1221},
    '94. Tetu': {'latitude': -0.2865, 'longitude': 37.2798},
    '95. Kieni': {'latitude': -0.3962, 'longitude': 37.2222},
    '96. Mathira': {'latitude': -0.4446, 'longitude': 37.2688},
    '97. Othaya': {'latitude': -0.5098, 'longitude': 37.2911},
    '98. Mukurweini': {'latitude': -0.5911, 'longitude': 37.2539},
    '99. Nyeri Town': {'latitude': -0.4233, 'longitude': 36.9566},
    '100. Nyandarua': {'latitude': -0.6364, 'longitude': 36.9884},
    '101. Kirinyaga Central': {'latitude': -0.9351, 'longitude': 37.2651},
    '102. Mwea': {'latitude': -0.6963, 'longitude': 37.4729},
    '103. Gichugu': {'latitude': -0.7133, 'longitude': 37.4699},
    '104. Kutus': {'latitude': -0.5975, 'longitude': 37.1585},
    '105. Kirinyaga South': {'latitude': -0.8636, 'longitude': 37.2534},
    '106. Mbeere': {'latitude': -1.0562, 'longitude': 37.5898},
    '107. Embu North': {'latitude': -0.5063, 'longitude': 37.5731},
    '108. Embu East': {'latitude': -0.4463, 'longitude': 37.5557},
    '109. Embu West': {'latitude': -0.3735, 'longitude': 37.4901},
    '110. Tharaka Nithi': {'latitude': -0.6188, 'longitude': 37.4539},
    '111. Bungoma': {'latitude': -0.4494, 'longitude': 34.5663},
    '112. Webuye East': {'latitude': -0.6292, 'longitude': 34.5677},
    '113. Webuye West': {'latitude': -0.6666, 'longitude': 34.5567},
    '114. Kimilili': {'latitude': -0.7244, 'longitude': 34.5523},
    '115. Kanduyi': {'latitude': -0.5711, 'longitude': 34.5717},
    '116. Bumula': {'latitude': -0.6137, 'longitude': 34.5711},
    '117. Mount Elgon': {'latitude': 1.1186, 'longitude': 34.7891},
    '118. Trans Nzoia': {'latitude': 1.0192, 'longitude': 34.7104},
    '119. Kiminini': {'latitude': 1.0497, 'longitude': 34.6962},
    '120. Cherangany': {'latitude': 1.0562, 'longitude': 34.6919},
    '121. Endebess': {'latitude': 1.0995, 'longitude': 34.6973},
    '122. Samburu East': {'latitude': 2.0991, 'longitude': 36.7463},
    '123. Samburu West': {'latitude': 2.6548, 'longitude': 36.7106},
    '124. Samburu North': {'latitude': 2.4251, 'longitude': 36.7339},
    '125. Marsabit South': {'latitude': 2.3392, 'longitude': 37.7986},
    '126. Marsabit Central': {'latitude': 2.3704, 'longitude': 37.9403},
    '127. Marsabit North': {'latitude': 2.2156, 'longitude': 37.7527},
    '128. Moyale': {'latitude': 3.5249, 'longitude': 39.0714},
    '129. Mandera South': {'latitude': 2.7463, 'longitude': 41.7062},
    '130. Mandera North': {'latitude': 3.2068, 'longitude': 41.8129},
    '131. Mandera East': {'latitude': 3.0734, 'longitude': 41.7348},
    '132. Lafey': {'latitude': 2.7349, 'longitude': 41.7322},
    '133. Wajir East': {'latitude': 1.6750, 'longitude': 40.0849},
    '134. Wajir North': {'latitude': 1.9975, 'longitude': 40.0733},
    '135. Wajir West': {'latitude': 1.6482, 'longitude': 39.7957},
    '136. Tana River': {'latitude': -2.6524, 'longitude': 39.8043},
    '137. Lamu East': {'latitude': -2.2471, 'longitude': 40.8724},
    '138. Lamu West': {'latitude': -2.3209, 'longitude': 40.7367},
    '139. Garissa Township': {'latitude': -0.4590, 'longitude': 39.6547},
    '140. Balambala': {'latitude': -0.8654, 'longitude': 39.4671},
    '141. Lagdera': {'latitude': -0.7101, 'longitude': 39.5473},
    '142. Dadaab': {'latitude': -0.0346, 'longitude': 40.0333},
    '143. Fafi': {'latitude': -0.0537, 'longitude': 40.4391},
    '144. Ijara': {'latitude': -1.0702, 'longitude': 40.1822},
    '145. Kirinyaga South': {'latitude': -0.8636, 'longitude': 37.2534},
    '146. Kirinyaga Central': {'latitude': -0.7133, 'longitude': 37.4699},
    '147. Gichugu': {'latitude': -0.7133, 'longitude': 37.4699},
    '148. Mbeere South': {'latitude': -0.7863, 'longitude': 37.6778},
    '149. Mbeere North': {'latitude': -0.9193, 'longitude': 37.6297},
    '150. Mwingi North': {'latitude': -0.1067, 'longitude': 38.1697},
    '151. Mwingi West': {'latitude': -0.1721, 'longitude': 38.2425},
    '152. Mwingi Central': {'latitude': -0.2357, 'longitude': 38.2103},
    '153. Kitui West': {'latitude': -1.2042, 'longitude': 38.0735},
    '154. Kitui Rural': {'latitude': -1.3273, 'longitude': 38.0895},
    '155. Kitui Central': {'latitude': -1.3147, 'longitude': 38.0902},
    '156. Kitui East': {'latitude': -1.2631, 'longitude': 38.2078},
    '157. Kitui South': {'latitude': -1.3075, 'longitude': 38.3243},
    '158. Masinga': {'latitude': -1.5062, 'longitude': 37.5965},
    '159. Yatta': {'latitude': -1.5307, 'longitude': 37.6611},
    '160. Kangundo': {'latitude': -1.3982, 'longitude': 37.5368},
    '161. Matungulu': {'latitude': -1.3192, 'longitude': 37.7035},
    '162. Kathiani': {'latitude': -1.3072, 'longitude': 37.7099},
    '163. Mavoko': {'latitude': -1.3469, 'longitude': 37.2357},
    '164. Machakos Town': {'latitude': -1.5198, 'longitude': 37.2621},
    '165. Mwala': {'latitude': -1.4956, 'longitude': 37.5054},
    '166. Mbooni': {'latitude': -1.5297, 'longitude': 37.4997},
    '167. Kilome': {'latitude': -1.5363, 'longitude': 37.6076},
    '168. Kaiti': {'latitude': -1.5246, 'longitude': 37.6575},
    '169. Makueni': {'latitude': -1.7781, 'longitude': 37.6988},
    '170. Kibwezi West': {'latitude': -2.5026, 'longitude': 37.6571},
    '171. Kibwezi East': {'latitude': -2.4692, 'longitude': 37.6375},
    '172. Kinangop': {'latitude': -0.7519, 'longitude': 37.1992},
    '173. Kipipiri': {'latitude': -0.6956, 'longitude': 37.2417},
    '174. Ol Kalou': {'latitude': -0.5671, 'longitude': 37.2267},
    '175. Ol Jorok': {'latitude': -0.5524, 'longitude': 37.0971},
    '176. Ndaragwa': {'latitude': -0.6019, 'longitude': 37.1221},
    '177. Tetu': {'latitude': -0.2865, 'longitude': 37.2798},
    '178. Kieni': {'latitude': -0.3962, 'longitude': 37.2222},
    '179. Mathira': {'latitude': -0.4446, 'longitude': 37.2688},
    '180. Othaya': {'latitude': -0.5098, 'longitude': 37.2911},
    '181. Mukurweini': {'latitude': -0.5911, 'longitude': 37.2539},
    '182. Nyeri Town': {'latitude': -0.4233, 'longitude': 36.9566},
    '183. Nyandarua': {'latitude': -0.6364, 'longitude': 36.9884},
    '184. Kirinyaga Central': {'latitude': -0.9351, 'longitude': 37.2651},
    '185. Mwea': {'latitude': -0.6963, 'longitude': 37.4729},
    '186. Gichugu': {'latitude': -0.7133, 'longitude': 37.4699},
    '187. Kutus': {'latitude': -0.5975, 'longitude': 37.1585},
    '188. Kirinyaga South': {'latitude': -0.8636, 'longitude': 37.2534},
    '189. Gikambura': {'latitude': -0.2718, 'longitude': 37.0456},
    '190. Ruiru': {'latitude': -1.1548, 'longitude': 37.0199},
    '191. Thika': {'latitude': -1.0332, 'longitude': 37.0663},
    '192. Gatundu North': {'latitude': -0.8323, 'longitude': 37.1751},
    '193. Gatundu South': {'latitude': -0.9447, 'longitude': 37.1317},
    '194. Juja': {'latitude': -1.0247, 'longitude': 37.0039},
    '195. Kiambu': {'latitude': -1.0000, 'longitude': 37.0226},
    '196. Kabete': {'latitude': -1.2244, 'longitude': 36.9087},
    '197. Kiambaa': {'latitude': -1.1829, 'longitude': 36.7874},
    '198. Limuru': {'latitude': -1.2797, 'longitude': 36.6444},
    '199. Ruiru': {'latitude': -1.1548, 'longitude': 37.0199},
    '200. Thika Town': {'latitude': -1.0332, 'longitude': 37.0663},
    '201. Gatanga': {'latitude': -0.7967, 'longitude': 37.2512},
    '202. Murang’a South': {'latitude': -0.6212, 'longitude': 37.2479},
    '203. Kandara': {'latitude': -0.7023, 'longitude': 37.2362},
    '204. Maragua': {'latitude': -0.5875, 'longitude': 37.2318},
    '205. Kangundo': {'latitude': -1.3982, 'longitude': 37.5368},
    '206. Matungulu': {'latitude': -1.3192, 'longitude': 37.7035},
    '207. Machakos Town': {'latitude': -1.5198, 'longitude': 37.2621},
    '208. Mwala': {'latitude': -1.4956, 'longitude': 37.5054},
    '209. Mbooni': {'latitude': -1.5297, 'longitude': 37.4997},
    '210. Kilome': {'latitude': -1.5363, 'longitude': 37.6076},
    '211. Kaiti': {'latitude': -1.5246, 'longitude': 37.6575},
    '212. Makueni': {'latitude': -1.7781, 'longitude': 37.6988},
    '213. Kibwezi West': {'latitude': -2.5026, 'longitude': 37.6571},
    '214. Kibwezi East': {'latitude': -2.4692, 'longitude': 37.6375},
    '215. Kathonzweni': {'latitude': -2.4309, 'longitude': 37.5822},
    '216. Mutito': {'latitude': -2.4716, 'longitude': 37.6265},
    '217. Nzaui': {'latitude': -2.4894, 'longitude': 37.6862},
    '218. Tharaka': {'latitude': -0.3673, 'longitude': 37.6356},
    '219. Chuka/Igambang’ombe': {'latitude': -0.1717, 'longitude': 37.5925},
    '220. Maara': {'latitude': -0.3742, 'longitude': 37.4871},
    '221. Meru Town': {'latitude': 0.0472, 'longitude': 37.6414},
    '222. Tigania West': {'latitude': -0.1487, 'longitude': 37.9366},
    '223. Tigania East': {'latitude': 0.0699, 'longitude': 37.8323},
    '224. Imenti North': {'latitude': 0.0699, 'longitude': 37.7216},
    '225. Imenti South': {'latitude': -0.0732, 'longitude': 37.7289},
    '226. Buuri': {'latitude': -0.2516, 'longitude': 37.7289},
    '227. South Imenti': {'latitude': -0.1632, 'longitude': 37.5919},
    '228. North Imenti': {'latitude': 0.1044, 'longitude': 37.6465},
    '229. Isiolo': {'latitude': 0.3490, 'longitude': 37.5951},
    '230. Merti': {'latitude': 0.5120, 'longitude': 38.0112},
    '231. Garbatulla': {'latitude': 0.6112, 'longitude': 37.7499},
    '232. Samburu North': {'latitude': 2.4251, 'longitude': 36.7339},
    '233. Samburu East': {'latitude': 2.6707, 'longitude': 36.8581},
    '234. Samburu West': {'latitude': 2.6548, 'longitude': 36.7106},
    '235. Marsabit South': {'latitude': 2.3392, 'longitude': 37.7986},
    '236. Marsabit Central': {'latitude': 2.3704, 'longitude': 37.9403},
    '237. Marsabit North': {'latitude': 2.2156, 'longitude': 37.7527},
    '238. Moyale': {'latitude': 3.5249, 'longitude': 39.0714},
    '239. Mandera South': {'latitude': 2.7463, 'longitude': 41.7062},
    '240. Mandera North': {'latitude': 3.2068, 'longitude': 41.8129},
    '241. Mandera East': {'latitude': 3.0734, 'longitude': 41.7348},
    '242. Lafey': {'latitude': 2.7349, 'longitude': 41.7322},
    '243. Wajir East': {'latitude': 1.6750, 'longitude': 40.0849},
    '244. Wajir North': {'latitude': 1.9975, 'longitude': 40.0733},
    '245. Wajir West': {'latitude': 1.6482, 'longitude': 39.7957},
    '246. Tana River': {'latitude': -2.6524, 'longitude': 39.8043},
    '247. Lamu East': {'latitude': -2.2471, 'longitude': 40.8724},
    '248. Lamu West': {'latitude': -2.3209, 'longitude': 40.7367},
    '249. Tana River': {'latitude': -2.6524, 'longitude': 39.8043},
    '250. Garissa Township': {'latitude': -0.4537, 'longitude': 39.6700},
    '251. Dadaab': {'latitude': 1.8467, 'longitude': 40.0192},
    '252. Fafi': {'latitude': -0.3311, 'longitude': 40.4013},
    '253. Lagdera': {'latitude': -0.0450, 'longitude': 40.4729},
    '254. Balambala': {'latitude': 0.5150, 'longitude': 40.5459},
    '255. Mandera Town': {'latitude': 3.1299, 'longitude': 41.8469},
    '256. Rhamu': {'latitude': 2.7985, 'longitude': 41.9429},
    '257. Moyale': {'latitude': 3.5249, 'longitude': 39.0714},
    '258. Wajir East': {'latitude': 1.6750, 'longitude': 40.0849},
    '259. Wajir North': {'latitude': 1.9975, 'longitude': 40.0733},
    '260. Wajir West': {'latitude': 1.6482, 'longitude': 39.7957},
    '261. Mandera South': {'latitude': 2.7463, 'longitude': 41.7062},
    '262. Marsabit South': {'latitude': 2.3392, 'longitude': 37.7986},
    '263. Marsabit Central': {'latitude': 2.3704, 'longitude': 37.9403},
    '264. Marsabit North': {'latitude': 2.2156, 'longitude': 37.7527},
    '265. Samburu East': {'latitude': 2.6707, 'longitude': 36.8581},
    '266. Samburu West': {'latitude': 2.6548, 'longitude': 36.7106},
    '267. Samburu North': {'latitude': 2.4251, 'longitude': 36.7339},
    '268. Isiolo': {'latitude': 0.3490, 'longitude': 37.5951},
    '269. Merti': {'latitude': 0.5120, 'longitude': 38.0112},
    '270. Garbatulla': {'latitude': 0.6112, 'longitude': 37.7499},
    '271. Chuka/Igambangombe': {'latitude': -0.1717, 'longitude': 37.5925},
    '272. Meru Town': {'latitude': 0.0472, 'longitude': 37.6414},
    '273. Tigania West': {'latitude': -0.1487, 'longitude': 37.9366},
    '274. Tigania East': {'latitude': 0.0699, 'longitude': 37.8323},
    '275. Imenti North': {'latitude': 0.0699, 'longitude': 37.7216},
    '276. Imenti South': {'latitude': -0.0732, 'longitude': 37.7289},
    '277. Buuri': {'latitude': -0.2516, 'longitude': 37.7289},
    '278. South Imenti': {'latitude': -0.1632, 'longitude': 37.5919},
    '279. North Imenti': {'latitude': 0.1044, 'longitude': 37.6465},
    '280. Kitui Central': {'latitude': -1.3592, 'longitude': 38.0733},
    '281. Kitui South': {'latitude': -1.3181, 'longitude': 38.2424},
    '282. Kitui Rural': {'latitude': -1.3545, 'longitude': 38.1739},
    '283. Mwingi Central': {'latitude': -1.0199, 'longitude': 38.2182},
    '284. Mwingi North': {'latitude': -1.2514, 'longitude': 38.1454},
    '285. Mwingi West': {'latitude': -1.3104, 'longitude': 38.0592},
    '286. Kibwezi East': {'latitude': -2.4692, 'longitude': 37.6375},
    '287. Kibwezi West': {'latitude': -2.5026, 'longitude': 37.6571},
    '288. Makueni': {'latitude': -1.7781, 'longitude': 37.6988},
    '289. Mutito': {'latitude': -2.4716, 'longitude': 37.6265},
    '290. Nzaui': {'latitude': -2.4894, 'longitude': 37.6862},
    '291. Kilome': {'latitude': -1.5363, 'longitude': 37.6076},
    '292. Mbooni': {'latitude': -1.5297, 'longitude': 37.4997},
    '293. Mwala': {'latitude': -1.4956, 'longitude': 37.5054},
    '294. Machakos Town': {'latitude': -1.5198, 'longitude': 37.2621},
    '295. Matungulu': {'latitude': -1.3192, 'longitude': 37.7035},
    '296. Kangundo': {'latitude': -1.3982, 'longitude': 37.5368},
    '297. Maragua': {'latitude': -0.5875, 'longitude': 37.2318},
    '298. Kandara': {'latitude': -0.7023, 'longitude': 37.2362},
    '299. Muranga South': {'latitude': -0.6212, 'longitude': 37.2479},
    '300. Gatanga': {'latitude': -0.7967, 'longitude': 37.2512},

}
# Mapping constituencies to their coordinates (latitude and longitude)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Or your dashboard page
    else:
        form = UserCreationForm()
    return render(request, 'maize/register.html', {'form': form})


def get_coordinates_for_constituency(constituency_name):
    return CONSTITUENCY_COORDINATES.get(constituency_name, None)

@login_required
def home(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            farmer = form.save()
            location_name = form.cleaned_data['location']
            coordinates = get_coordinates_for_constituency(location_name)

            # Build API parameters depending on whether we have lat/lon
            if coordinates:
                params = {
                    'lat': coordinates['latitude'],
                    'lon': coordinates['longitude'],
                    'appid': settings.OPENWEATHER_API_KEY
                }
            else:
                # fallback to city name query
                params = {
                    'q': location_name,
                    'appid': settings.OPENWEATHER_API_KEY
                }

            # Fetch weather
            try:
                r = requests.get('http://api.openweathermap.org/data/2.5/weather', params=params)
                r.raise_for_status()
                weather_data = r.json()
                rain = weather_data.get('rain', {}).get('1h', 0)
            except Exception:
                rain = 0

            # Prepare features and predict
            features = [[
                farmer.farm_size,
                farmer.elevation,
                farmer.soil_type_index(),
                rain
            ]]
            risk_pred = flood_risk_model.predict(features)[0]
            yield_loss = yield_loss_model.predict(features)[0]
            risk_label = ['Low', 'Moderate', 'High'][risk_pred]

            if risk_label == 'Low':
                recommendation = """
                <b>Recommended drought‑tolerant maize varieties:</b><br>
                1. <b>Drought Tego®</b> – WE1101, WE2101 (WEMA Project)<br>
                2. <b>DK8031</b> – Hybrid from Bayer (early-maturing)<br>
                3. <b>KH500-46A</b> – Kenya Seed Co<br>
                4. <b>KDV4</b> – Katumani OPV for arid zones<br>
                """
            elif risk_label == 'Moderate':
                recommendation = "Rainfall is moderate. You can use <b>standard maize varieties</b> suited to your region."
            else:  # High risk
                recommendation = """
                <b>Recommended flood‑tolerant maize varieties:</b><br>
                1. <b>H664</b> – Kenya Seed Company; tolerates waterlogging<br>
                2. <b>H6213</b> – Good for high rainfall areas<br>
                3. <b>SC Simba 60</b> – By Seed Co, adapted to wet climates<br>
                4. <b>KH500-31A</b> – Kenya Seed Co; strong roots, less lodging<br>
                """

            # Save and render results
            risk = FloodRisk.objects.create(
                farmer=farmer,
                risk_level=risk_label,
                yield_loss_estimate=round(yield_loss, 2),
                recommendation=recommendation
            )


            return render(request, 'maize/results.html', {
                'risks': [  # if you want to show just this one
                    {
                      'risk_id': risk.id,
                      'farmer': farmer,
                      'risk_level': risk_label,
                      'yield_loss_estimate': round(yield_loss,2),
                      'recommendation': recommendation,
                      'date_predicted': datetime.datetime.now()

                    }
                ]
            })

    else:
        form = FarmerForm()

    return render(request, 'maize/home.html', {'form': form})

@login_required
def results(request):
    risks = FloodRisk.objects.all().order_by('-date_predicted')[:5]
    return render(request, 'maize/results.html', {'risks': risks})

def index(request):
    return render(request, 'maize/index.html')