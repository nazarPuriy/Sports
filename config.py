from decouple import config


class Config:
  pass


class ProductionConfig(Config):
  DEBUG = False
  SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default='localhost')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  STATIC_FOLDER = "/static"
  TEMPLATE_FOLDER = "/templates"
  SECRET_KEY = config('SECRET_KEY', default='localhost')


class DevelopmentConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = 'postgresql://gghqarlmozkirg:24c8e44abbc90553b6cc42119ab44f1ce32b9d4a754e72cbe090f753a04e33b7@ec2-3-211-6-217.compute-1.amazonaws.com:5432/d2smoids43novu'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  STATIC_FOLDER = "/P2_VUE_WEBPACK/frontend/dist/static"
  TEMPLATE_FOLDER = "/P2_VUE_WEBPACK/frontend/dist"
  SECRET_KEY = "1q2s3f5g7jggujbffrhnbcdgh78jbhd"


config = {
  'development': DevelopmentConfig,
  'production': ProductionConfig
}
