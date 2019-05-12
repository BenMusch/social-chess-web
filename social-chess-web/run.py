from app import app
from flask_debugtoolbar import DebugToolbarExtension

app.config['DEBUG'] = True

toolbar = DebugToolbarExtension(app)

#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.run(host="0.0.0.0", port=8080, debug=True)
