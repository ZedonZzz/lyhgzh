from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import config
from volcenginesdkarkruntime import Ark

client = Ark(
    api_key = "bd8963b1-a15b-4497-8ac5-30f9f2a08b74",  #ARK_API_KEY 需要替换为您在平台创建的 API Key
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

# 因MySQLDB不支持Python3，使用pymysql扩展库代替MySQLDB库
pymysql.install_as_MySQLdb()

# 初始化web应用
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = config.DEBUG
app.config['JSON_AS_ASCII'] = False

# 设定数据库链接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/flask_demo'.format(config.username, config.password,
                                                                             config.db_address)

# 初始化DB操作对象
db = SQLAlchemy(app)

# 加载控制器
from wxcloudrun import views

# 加载配置
app.config.from_object('config')
