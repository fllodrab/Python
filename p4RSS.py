#!/usr/bin/python
# -*- coding: utf-8 -*-

from web.contrib.template import render_mako
import web
from web import form
from pymongo import Connection
import pymongo
import feedparser
import urllib
import datetime
from time import time
import tweepy



# Para poder usar sesiones con web.py
web.config.debug = False

urls = (
	'/', 'index',
	'/about', 'about',
	'/features', 'features',
	'/news', 'news',
	'/contact', 'contact',
	'/formularioLogin', 'formularioLogin',
	'/formularioSignUP', 'formularioSignUP',
	'/formularioMod', 'formularioMod',
	'/logout', 'logout',
	'/registrado', 'registrado',
	'/modificado', 'modificado',
	'/post', 'post',
	'/modificado1', 'modificado1',
	'/RSS', 'RSS',
	'/formularioChart', 'formularioChart',
	'/Geomap', 'Geomap',
	'/searchMap', 'searchMap',
	'/Twitter', 'Twitter',
	'/formularioTwitter', 'formularioTwitter',
	)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'usuario':'','time':''})

# Templates de Mako
render = render_mako(
        directories=['temp/'],
        input_encoding='utf-8',
        output_encoding='utf-8',
        )

login = form.Form(
	form.Textbox("Usuario", form.notnull, description = "Usuario"),
	form.Password("Password", form.notnull, description = "Password"),
	form.Button("Sign in", description = "Sign in"),
)

Email = form.regexp(r'(\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b)', 'El e-mail tiene que tener la forma miemail@servidormail.com')
Visa = form.regexp(r'([0-9]{4}) ([0-9]{4}) ([0-9]{4}) ([0-9]{4})|([0-9]{4})-([0-9]{4})-([0-9]{4})-([0-9]{4})', '4 grupos de 4 digitos separados por un espacio o -')

# Formulario
signUP = form.Form(
	form.Textbox("Nombre", form.notnull, description = "Nombre"),
	form.Textbox("Apellidos", form.notnull, description = "Apellidos"),
	form.Textbox("email", Email, description = "E-mail"),
	form.Dropdown('Dia', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], description="Dia"),
	form.Dropdown('Mes', [('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo','Marzo'), ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'), ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'), ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre','Diciembre')], description = "Mes"),
	form.Dropdown('Ano', [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013], description= "Anio"),
	form.Textarea("Direccion", form.notnull, description = "Direccion",),
	form.Password("Contrasena", form.notnull, description = "Contrasenia"),
	form.Password("ReContrasena", form.notnull, description = "Reescribe contrasenia"),
	form.Radio("MetodoDePago", [('Reembolso', 'Reembolso'),('VISA','VISA')], form.Validator('Tienes que seleccionar un metodo de pago', lambda x:'MetodoDePago' not in x), description = "Metodo de Pago"),
	form.Textbox("numVisa", Visa, description = "Numero tarjeta VISA"),
	form.Checkbox("AceptoClausula", form.Validator('Tienes que aceptar las clausulas', lambda i:'AceptoClausula' not in i), description = "Acepto las clausulas de proteccion de datos"),
	form.Button("Enviar"),
	validators = [
		form.Validator("*Las contraseñas no coinciden.", lambda y: y.Contrasena == y.ReContrasena),
		form.Validator("*Tamanio minimo 7 en contrasenia", lambda i: len(str(i.Contrasena)) >=7 ), 
    	#form.Validator("*fecha nacimiento incorrecta", lambda i: i.Mes=="enero" or i.Mes=="marzo" or i.Mes=="mayo" or i.Mes=="julio" or i.Mes=="agosto" or i.Mes=="octubre" or i.Mes=="diciembre" or (i.Mes=="abril" and int(i.Dia) < 31) or (i.Mes=="junio" and int(i.Dia) < 31) or (i.Mes=="septiembre" and int(i.Dia) < 31) or (i.Mes=="noviembre" and int(i.Dia) < 31) or (i.Mes=="febrero" and int(i.Dia) < 29) or (i.Mes=="febrero" and int(i.Ano) % 4 == 0 and int(i.Dia) < 30))
    	]
)

mod = form.Form(
	form.Textbox("Nombre", form.notnull, description = "Nombre"),
	form.Textbox("Apellidos", form.notnull, description = "Apellidos"),
	form.Textbox("email", Email, description = "E-mail"),
	form.Dropdown('Dia', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], description="Dia"),
	form.Dropdown('Mes', [('Enero', 'Enero'), ('Febrero', 'Febrero'), ('Marzo','Marzo'), ('Abril', 'Abril'), ('Mayo', 'Mayo'), ('Junio', 'Junio'), ('Julio', 'Julio'), ('Agosto', 'Agosto'), ('Septiembre', 'Septiembre'), ('Octubre', 'Octubre'), ('Noviembre', 'Noviembre'), ('Diciembre','Diciembre')], description = "Mes"),
	form.Dropdown('Ano', [1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013], description= "Anio"),
	form.Textarea("Direccion", form.notnull, description = "Direccion",),
	form.Password("Contrasena", form.notnull, description = "Contrasenia"),
	form.Password("ReContrasena", form.notnull, description = "Reescribe contrasenia"),
	form.Radio("MetodoDePago", [('Reembolso', 'Reembolso'),('VISA','VISA')], form.Validator('Tienes que seleccionar un metodo de pago', lambda x:'MetodoDePago' not in x), description = "Metodo de Pago"),
	form.Textbox("numVisa", Visa, description = "Numero tarjeta VISA"),
	form.Checkbox("AceptoClausula", form.Validator('Tienes que aceptar las clausulas', lambda i:'AceptoClausula' not in i), description = "Acepto las clausulas de proteccion de datos"),
	form.Button("Enviar"),
	validators = [
		form.Validator("*Las contraseñas no coinciden.", lambda y: y.Contrasena == y.ReContrasena),
		form.Validator("*Tamanio minimo 7 en contrasenia", lambda i: len(str(i.Contrasena)) >=7 ), 
    	#form.Validator("*fecha nacimiento incorrecta", lambda i: i.Mes=="enero" or i.Mes=="marzo" or i.Mes=="mayo" or i.Mes=="julio" or i.Mes=="agosto" or i.Mes=="octubre" or i.Mes=="diciembre" or (i.Mes=="abril" and int(i.Dia) < 31) or (i.Mes=="junio" and int(i.Dia) < 31) or (i.Mes=="septiembre" and int(i.Dia) < 31) or (i.Mes=="noviembre" and int(i.Dia) < 31) or (i.Mes=="febrero" and int(i.Dia) < 29) or (i.Mes=="febrero" and int(i.Ano) % 4 == 0 and int(i.Dia) < 30))
    	]
)

### Formulario Google Charts ###
chart = form.Form(
	form.Textbox("Nacionalidad", form.notnull, description = "Nacionalidad"),
	form.Textbox("Numero", form.notnull, description = "Numero"),
	form.Button("Enviar"),
)

twitter = form.Form(
	form.Textbox("Busqueda",form.notnull,description = "Busqueda"),
	form.Button("Buscar"),
)

def comprueba_identificacion (): 
	usuario = session.usuario   # Devuelve '' cuando no está identificado
	return usuario              # que es el usuario inicial 

class logout:
	def GET(self):
		usuario = session.usuario
		session.kill()
		return 'adios ' + usuario

class index:
	def GET(self):
		fL = login()		# Hacemos copia del formulario
		fS = signUP()		# Hacemos copia del segundo formulario
		usuario = session.usuario
		if usuario:
			return render.features(Usuario=session.usuario)
		else:
			return render.index(formL=fL.render(), formS=fS.render())

class formularioLogin:
	#def GET(self):
	#	form = login()
	#	return render.formularioLogin(formL)

	def POST(self):
		fL = login() 
		fS = signUP()
		if not fL.validates():
			return render.index(formL=fL.render(), formS=fS.render())
		
		i = web.input()
		usuario  = i.Usuario
		password = i.Password

		try:
			con = pymongo.Connection()
		except pymongo.errors.ConnectionFailure, e:
			print "no se pudo conectar a mongoDB: %s" % e

		db = con.registros
		collection = db.my_collection

		consulta = collection.find_one({'usuario': usuario, 'Contrasenia': password})
		if consulta:
			session.usuario = usuario
			return render.features(Usuario=session.usuario)
		else:
			form = login()
			return render.index(formL=fL.render(), formS=fS.render())

		# if password == "llodra" :
		#	if usuario == "llodra":
		#		session.usuario = usuario
		#		return render.features(Usuario=session.usuario)	
		#else:
		#	form = login()
		#	return render.index(formL=fL.render(), formS=fS.render())

class formularioSignUP:
	#def GET(self):
	#	form = signUP()
	#	return render.formularioSignUP(form)

	def POST(self):
		fL = login()
		fS = signUP()

		if not fS.validates():
			return render.index(formL=fL.render(), formS=fS.render())
		else:
			try:
				con = pymongo.Connection()
			except pymongo.errors.ConnectionFailure, e:
				print "no se pudo conectar a mongoDB: %s" % e

			db = con.registros		#Creamos nuestra base de datos
			collection = db.my_collection
			doc = {'usuario':fS.d.Nombre, 'Apellidos':fS.d.Apellidos, 'email':fS.d.email, 'Dia':fS.d.Dia, 'Mes':fS.d.Mes, 'Ano':fS.d.Ano, 'Direccion':fS.d.Direccion, 'Contrasenia':fS.d.Contrasena, 'MetodoDePago':fS.d.MetodoDePago, 'numVisa':fS.d.numVisa}
			collection.insert(doc)

			session.usuario = fS.d.Nombre
			return render.registrado(Usuario=fS.d.Nombre)

class about:
	def GET(self):
		return render.about(Usuario=session.usuario)

class features:
	def GET(self):
		if session.usuario == '':
			return render.index(formL=fL.render(), formS=fS.render())
		else:
			return render.features(Usuario=session.usuario)

class news:
	def GET(self):
		googleC = chart()
		
		return render.news(Usuario=session.usuario, formGC=googleC.render())

	#def POST(self):
	#	googleC = chart()		# Hacemos copia del formulario

#		if not googleC.validates():
#			return render.news(Usuario=session.usuario, formGC=googleC.render())
#		else:
#			try:
#				con=pymongo.Connection()
#			except pymongo.errors.ConnectionFailure, e:
#				print "No se pudo conectar a MongoDB: %s" % e 
#
#			db = con.charts
#			collection = db.my_collection
#			doc = {'Nacion':chart.d.Nacionalidad, 'Numero':chart.d.Numero}
#			collection.insert(doc)
			
#			return render.post(Usuario=usuario, Nacion=chart_nacion, Numero=chart_numero)

class post:
	def GET(self):
		usuario = session.usuario
		chart_nacion = []
		chart_numero = []

		try:
			con = pymongo.Connection()
		except pymongo.errors.ConnectionFailure, e:
			print "no se pudo conectar a mongoDB: %s" % e

		db = con.charts
		collection = db.my_collection

		for get in collection.find():
			print get['Nacion']
			print get['Numero']
			chart_nacion.append(get['Nacion'])
			chart_numero.append(get['Numero'])

		return render.post(Usuario=usuario, Nacion=chart_nacion, Numero=chart_numero)


class formularioChart:
	def POST(self):
		googleC = chart()		# Hacemos copia del formulario
		usuario = session.usuario
		if not googleC.validates():
			return render.news(Usuario=session.usuario, formGC=googleC.render())
		else:
			try:
				con=pymongo.Connection()
			except pymongo.errors.ConnectionFailure, e:
				print "No se pudo conectar a MongoDB: %s" % e 

			db = con.charts
			collection = db.my_collection
			doc = {'Nacion':googleC.d.Nacionalidad, 'Numero':googleC.d.Numero}

			collection.insert(doc)
			
			return render.news(Usuario=usuario, formGC=googleC.render())


class contact:
	def GET(self):
		return render.conctact(Usuario=session.usuario)

class registrado:
	def GET(self):
		return render.registrado(Usuario=session.usuario)

class modificado:
	def GET(self):
		modificar = mod()

		usuario = session.usuario
		if usuario:
			return render.modificado1(nombre=consulta['usuario'], apellidos=consulta['Apellidos'], correo_electronico=consulta['email'], direccion=consulta['Direccion'], dia=consulta['Dia'], mes=consulta['Mes'], anio=consulta['Ano'], forma_pago=consulta['MetodoDePago'], password=consulta['Contrasenia'], num_visa=consulta['numVisa'], Usuario=session.usuario)
		else:
			return render.modificado(fMod=modificar.render())

class modificado1:
	def GET(self):
		usuario = session.usuaario

		try:
			con=pymongo.Connection()
		except pymongo.errors.ConnectionFailure, e:
			print "No se pudo conectar a MongoDB: %s" % e 

		db = con.usuarios
		collection = db.my_collection

		consulta = collection.find_one({'usuario':usuario})
		if consulta:
			return render.modificado1(nombre=consulta['usuario'], apellidos=consulta['Apellidos'], correo_electronico=consulta['email'], direccion=consulta['Direccion'], dia=consulta['Dia'], mes=consulta['Mes'], anio=consulta['Ano'], forma_pago=consulta['MetodoDePago'], password=consulta['Contrasenia'], num_visa=consulta['numVisa'], Usuario=session.usuario)         

class formularioMod:
	def POST(self):
		modificar = mod()

		if not modificar.validates():
			return render.modificado(Usuario = session.usuario)
		else:
			try:
				con = pymongo.Connection()
			except pymongo.errors.ConnectionFailure, e:
				print "no se pudo conectar a mongoDB: %s" % e

			db = con.registros		#Creamos nuestra base de datos
			collection = db.my_collection
			doc = {'usuario':mod.d.Nombre, 'Apellidos':modificar.d.Apellidos, 'email':modificar.d.email, 'Dia':modificar.d.Dia, 'Mes':modificar.d.Mes, 'Ano':modificar.d.Ano, 'Direccion':modificar.d.Direccion, 'Contrasenia':modificar.d.Contrasena, 'MetodoDePago':modificar.d.MetodoDePago, 'numVisa':modificar.d.numVisa}
			collection.update(doc)

			session.usuario = modificar.d.Nombre
			return render.modificado1(nombre=consulta['usuario'], apellidos=consulta['Apellidos'], correo_electronico=consulta['email'], direccion=consulta['Direccion'], dia=consulta['Dia'], mes=consulta['Mes'], anio=consulta['Ano'], forma_pago=consulta['MetodoDePago'], password=consulta['Contrasenia'], num_visa=consulta['numVisa'], Usuario=modificar.d.Nombre)

class RSS:
	def GET(self):
		newsDB = []		#Lista para ir metiendo RSS en nuestra base de datos

		try:
			con = pymongo.Connection()
		except pymongo.errors.ConnectionFailure, e:
			print "no se pudo conectar a mongoDB: %s" % e

		db = con.rss_noticias		#Creamos nuestra base de datos
		collection = db.my_collection
		collection.remove()			#Limpiamos la base de datos para no almacenar tanto

		d = feedparser.parse('http://www.theverge.com/rss/frontpage')

		for item in d.entries:
			collection.insert({'rss':item["title"]})

		contador = len(d['entries'])

		for get in collection.find():
			newsDB.append(get['rss'])
		return render.RSS(Usuario=session.usuario, contador=contador, noticias=newsDB)

class Geomap:
	def GET(self):
		return render.map(Usuario=session.usuario)

class searchMap:
	def GET(self):
		return render.searchMap(Usuario=session.usuario)

class formularioTwitter:
	def POST(self):
		formTwit = twitter()
		usuario = session.usuario
		twitName = []
		twitPhoto = []
		twitText = []

		if not formTwit.validates():
			return render.searchMap(Usuario = session.usuario)
		else:

			consumer_key = 'YK34cNgoB9vaT9ugUcvWkA'
			consumer_secret = '3DaRYJtuoLYW11AxjWvustDphF77wRVt4q7fXTCw'
			access_token = '242933164-TEmqeKCIlAghAcM6RifKdWf8jhonFL2ExSGGI8R2'
			access_token_secret = 'iHxZrQS2mvCDxG4phNRJpZcXVLqH9GItREYwZpcI9QjkT'

			auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_token, access_token_secret)
			# Creation of the actual interface, using authentication
			api = tweepy.API(auth)
			# https://dev.twitter.com/docs/api/1.1/get/search/tweets
			tweets = api.search(q=str(formTwit.d.Busqueda), count=10)
			for i in tweets:
				twitName.append(i.author.name)
				twitPhoto.append(i.author.profile_image_url)
				twitText.append(i.text)

			return render.Twitter(Usuario=session.usuario, Nomtwit=twitName, Fottwit=twitPhoto, Texttwit=twitText, formT=formTwit.render())

class Twitter:
	def GET(self):
		formTwit = twitter()
		twitName = []
		twitPhoto = []
		twitText = []

		consumer_key = 'YK34cNgoB9vaT9ugUcvWkA'
		consumer_secret = '3DaRYJtuoLYW11AxjWvustDphF77wRVt4q7fXTCw'
		access_token = '242933164-TEmqeKCIlAghAcM6RifKdWf8jhonFL2ExSGGI8R2'
		access_token_secret = 'iHxZrQS2mvCDxG4phNRJpZcXVLqH9GItREYwZpcI9QjkT'

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		# Creation of the actual interface, using authentication
		api = tweepy.API(auth)
		# https://dev.twitter.com/docs/api/1.1/get/search/tweets
		tweets = api.search(q='Granada', count=10)

		for i in tweets:
			twitName.append(i.author.name)
			twitPhoto.append(i.author.profile_image_url)
			twitText.append(i.text)
		# Mostramos los campos del objeto Tweet
		#print dir(tweets[0])
		# Mostramos los campos del objeto author del Tweet
		#print dir(tweets[0].author)
		# Mostramos el nombre del Autor del Tweet.
		#print tweets[0].author.name
		# Mostrar texto
		#print tweets[0].text
		count = 10

		return render.Twitter(Usuario=session.usuario, Nomtwit=twitName, Fottwit=twitPhoto, Texttwit=twitText, formT=formTwit.render())

if __name__ == '__main__':
    app.run()

    
