from flask import Blueprint, request, jsonify, make_response, current_app
import numpy as np
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.resnet50 import preprocess_input
# from PIL import Image
# import io
import base64
import os
bp = Blueprint('chohai', __name__)

# 类别映射
category_translation = {
    "Apple___Apple_scab": "苹果黑星病",
    "Apple___Black_rot": "苹果黑腐病",
    "Apple___Cedar_apple_rust": "苹果雪松锈病",
    "Apple___healthy": "苹果健康",
    "Blueberry___healthy": "蓝莓健康",
    "Cherry_(including_sour)___Powdery_mildew": "樱桃白粉病",
    "Cherry_(including_sour)___healthy": "樱桃健康",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "玉米灰斑病",
    "Corn_(maize)___Common_rust_": "玉米普通锈病",
    "Corn_(maize)___Northern_Leaf_Blight": "玉米北方叶枯病",
    "Corn_(maize)___healthy": "玉米健康",
    "Grape___Black_rot": "葡萄黑腐病",
    "Grape___Esca_(Black_Measles)": "葡萄黑麻疹病",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "葡萄叶枯病",
    "Grape___healthy": "葡萄健康",
    "Orange___Haunglongbing_(Citrus_greening)": "柑橘黄龙病",
    "Peach___Bacterial_spot": "桃细菌性斑点病",
    "Peach___healthy": "桃健康",
    "Pepper,_bell___Bacterial_spot": "甜椒细菌性斑点病",
    "Pepper,_bell___healthy": "甜椒健康",
    "Potato___Early_blight": "马铃薯早疫病",
    "Potato___Late_blight": "马铃薯晚疫病",
    "Potato___healthy": "马铃薯健康",
    "Raspberry___healthy": "树莓健康",
    "Soybean___healthy": "大豆健康",
    "Squash___Powdery_mildew": "南瓜白粉病",
    "Strawberry___Leaf_scorch": "草莓叶枯病",
    "Strawberry___healthy": "草莓健康",
    "Tomato___Bacterial_spot": "番茄细菌性斑点病",
    "Tomato___Early_blight": "番茄早疫病",
    "Tomato___Late_blight": "番茄晚疫病",
    "Tomato___Leaf_Mold": "番茄叶霉病",
    "Tomato___Septoria_leaf_spot": "番茄斑枯病",
    "Tomato___Spider_mites Two_spotted_spider_mite": "番茄红蜘蛛",
    "Tomato___Target_Spot": "番茄靶斑病",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "番茄黄化曲叶病毒",
    "Tomato___Tomato_mosaic_virus": "番茄花叶病毒",
    "Tomato___healthy": "番茄健康"
}

# 加载模型
# model = load_model('models/plant_model.h5')

# 病虫害诊断信息
disease_info = {
    "苹果黑星病": {
        "diagnosis": "苹果黑星病是由真菌Venturia inaequalis引起的，主要危害苹果叶片和果实。病斑初期为淡黄色，后期变为黑色绒状霉层。",
        "treatment": "1. 清除病叶、病果，减少病原菌越冬基数\n2. 春季萌芽前喷施石硫合剂\n3. 发病初期喷施苯醚甲环唑、戊唑醇等杀菌剂\n4. 选择抗病品种种植"
    },
    "苹果黑腐病": {
        "diagnosis": "苹果黑腐病是由真菌Botryosphaeria obtusa引起的，主要危害果实、叶片和枝条。病斑呈褐色至黑色，有同心轮纹。",
        "treatment": "1. 清除病枝、病果，减少病原\n2. 加强果园管理，增强树势\n3. 果实套袋保护\n4. 喷施代森锰锌、嘧菌酯等杀菌剂"
    },
    "苹果雪松锈病": {
        "diagnosis": "苹果雪松锈病是由真菌Gymnosporangium yamadae引起的转主寄生菌，需在苹果和桧柏上交替寄生完成生活史。",
        "treatment": "1. 清除果园周围的桧柏等转主寄主\n2. 早春喷施三唑酮或戊唑醇\n3. 发病初期喷施嘧菌酯、吡唑醚菌酯\n4. 加强果园通风透光"
    },
    "玉米灰斑病": {
        "diagnosis": "玉米灰斑病是由真菌Cercospora zeae-maydis引起的叶部病害，病斑呈长条形，灰褐色，严重时导致叶片枯死。",
        "treatment": "1. 选用抗病品种\n2. 合理密植，保证通风透光\n3. 发病初期喷施苯醚甲环唑、嘧菌酯\n4. 收获后深翻土地，减少病原"
    },
    "玉米普通锈病": {
        "diagnosis": "玉米普通锈病是由真菌Puccinia sorghi引起的，病斑呈圆形或椭圆形，红褐色，表皮破裂后散出铁锈色粉末。",
        "treatment": "1. 选用抗病品种\n2. 合理施肥，增施磷钾肥\n3. 发病初期喷施三唑酮、戊唑醇\n4. 清除田间病残体"
    },
    "番茄细菌性斑点病": {
        "diagnosis": "番茄细菌性斑点病是由细菌Pseudomonas syringae pv. tomato引起的，叶片上出现水渍状小斑点，后期变为褐色坏死斑。",
        "treatment": "1. 选用无病种子，种子消毒\n2. 轮作倒茬，避免连作\n3. 发病初期喷施氢氧化铜、春雷霉素\n4. 控制田间湿度，避免大水漫灌"
    },
    "番茄晚疫病": {
        "diagnosis": "番茄晚疫病是由真菌Phytophthora infestans引起的毁灭性病害，叶片出现水渍状病斑，湿度大时产生白色霉层。",
        "treatment": "1. 选用抗病品种\n2. 高畦栽培，合理密植\n3. 发病初期喷施烯酰吗啉、氟噻唑吡乙酮\n4. 及时清除中心病株"
    },
    "玉米健康": {
        "diagnosis": "玉米植株生长健康，无病虫害迹象。叶片呈鲜绿色，茎秆粗壮，根系发达。",
        "treatment": "1. 保持合理密植\n2. 定期施肥，保证营养供应\n3. 注意水分管理，避免旱涝\n4. 定期巡查，预防病虫害发生"
    },
    "苹果健康": {
        "diagnosis": "苹果树生长旺盛，叶片浓绿有光泽，无病虫害迹象。果实发育良好，树势强壮。",
        "treatment": "1. 合理修剪，保持通风透光\n2. 定期施肥，保证营养均衡\n3. 注意水分管理，避免干旱\n4. 定期巡查，预防病虫害发生"
    }
}


# @bp.route('/detect', methods=['POST'])
# def detect_disease():
#     try:
#         # 获取图像数据
#         data = request.get_json()
#         image_data = data['image']
#
#         # 从base64字符串中提取图像数据
#         header, encoded = image_data.split(",", 1)
#         binary_data = base64.b64decode(encoded)
#
#         # 将二进制数据转换为图像
#         img = Image.open(io.BytesIO(binary_data))
#         img = img.resize((224, 224))
#
#         # 预处理图像
#         img_array = image.img_to_array(img)
#         img_array = np.expand_dims(img_array, axis=0)
#         img_array = preprocess_input(img_array)
#
#         # 进行预测
#         predictions = model.predict(img_array)
#         predicted_class_index = np.argmax(predictions, axis=1)[0]
#         confidence = predictions[0][predicted_class_index] * 100
#
#         # 获取类别名称
#         class_names = list(category_translation.keys())
#         predicted_class = class_names[predicted_class_index]
#         disease_name = category_translation[predicted_class]
#
#         # 获取诊断信息和防治建议
#         diagnosis = disease_info.get(disease_name, {}).get("diagnosis", "暂无诊断信息")
#         treatment = disease_info.get(disease_name, {}).get("treatment", "暂无防治建议")
#
#         return jsonify({
#             "disease": disease_name,
#             "confidence": f"{confidence:.2f}",
#             "diagnosis": diagnosis,
#             "treatment": treatment
#         })
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500