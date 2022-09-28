# -*- coding: utf-8 -*-

import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Deteccion_cambios_imagenes_radar"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Deteccion de cambios para imagenes radar"
        self.description = "Esta herramienta permite contrastar dos imagenes de radar principalmente Sentinel 1 que sean de diferentes fechas y detectar cambios en las coberturas"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        imagen_1_entrada = arcpy.Parameter(
            displayName="Ingrese la primera imagen",
            name="raster_1_entrada",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")
        
        imagen_2_entrada = arcpy.Parameter(
            displayName="Ingrese la segunda imagen",
            name="raster_2_entrada",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        carpeta_destino = arcpy.Parameter(
            displayName="Seleccione la carpeta de destino",
            name="output_raster",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        
        tipo_filtro = arcpy.Parameter(
            displayName="Seleccione el tipo de filtro",
            name="tipo_filtro",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        tipo_filtro.filter.type = "ValueList"
        tipo_filtro.filter.list = ["Lee", "Lee Enriquecido", "Frost", "Kuan"]
        tipo_filtro.value = "Kuan"

        tamano_filtro = arcpy.Parameter(
            displayName="Seleccione el tamaño del filtro",
            name="tamaño_filtro",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")

        tamano_filtro.filter.type = "ValueList"
        tamano_filtro.filter.list = ["3x3", "5x5", "7x7", "9x9", "11x11"]
        tamano_filtro.value = "3*3"

        ruido_modelo = arcpy.Parameter(
            displayName = "Seleccionar el tipo de ruido del modelo",
            name="ruido_modelo",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        ruido_modelo.enabled = False

        ruido_modelo.filter.type = "ValueList"
        ruido_modelo.filter.list = ["Aditivo", "Multiplicativo", "Aditivo y Multiplicativo"]
        ruido_modelo.vaue = "Multiplicativo"

        var_ruido = arcpy.Parameter(
            displayName="Especifique la varianza del ruido",
            name="varianza_imagen",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        var_ruido.enabled = False
        var_ruido.value = None

        media_aditivo = arcpy.Parameter(
            displayName="Especifique la media de ruido aditivo",
            name="media_ruido_aditivo",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")
        media_aditivo.enabled = False
        media_aditivo.value = None

        media_multiplicativo = arcpy.Parameter(
            displayName = "Especifique la media del ruido multiplicativo",
            name="media_ruido_multiplicativo",
            datatype="GPDouble",
            parameterType="Optional",
            direction="Input")

        media_multiplicativo.enabled = False
        media_multiplicativo.value = 1

        nlooks = arcpy.Parameter(
            displayName = "Especifique el numero de aspectos de la Imagen",
            name="nlooks",
            datatype="GPLong",
            parameterType="Optonal",
            direction="Input")
        nlooks.enabled = False
        nlooks.value = 1

        factor_amortiguacion = arcpy.Parameter(
            displayName="Especifique el factor de amortiguacion",
            name="factor_humedad",
            datatype="GPDouble",
            parameterType="Optional",
            direction ="Input")
        factor_amortiguacion.enabled = False
        factor_amortiguacion.value = None

        params = [imagen_1_entrada,imagen_2_entrada, carpeta_destino, tipo_filtro,tamano_filtro,ruido_modelo,var_ruido, media_aditivo,
                  media_multiplicativo, nlooks, factor_amortiguacion]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if params[3].valueAsText == "Lee":
            for p in params[5:6]:
                p.enabled = True

            if params[5].valueAsText == "Aditivo" or params[5].valueAsText == "Aditivo y Multiplicativo":
                for p in params[6:9]:
                    p.enabled = True
                for p in params[9:]:
                    p.enabled = False

            elif params[5].valueAsText == "Multiplicativo":
                for p in params[6:9]:
                    p.enabled = False
                for p in params[9:10]:
                    p.enabled = True
                for p in params[10:]:
                    p.enabled = False

            elif params[3].valueAsText == "Lee Enriquecido":
                for p in params[5:10]:
                    p.enabled = False
                for p in params[10:]:
                    p.enabled = True

            elif params[3].valueAsText == "Frost":
                for p in params[5:10]:
                    p.enabled = False
                for p in params[10:]:
                    p.enabled = True

            elif params[0].valueAsText == "Kuan":
                for p in params[5:9]:
                    p.enabled = False
                for p in params[9:10]:
                    p.enabled = True
                for p in params[10:]:
                    p.enabled = False
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        self.updateParameters(params)

        imagen_1_entrada = params[0].valueAsText
        imagen_2_entrada = params[1].valueAsText
        carpeta_destino = params[2].valueAsText
        tipo_filtro = params[3].valueAsText
        tamano_filtro = params[4].valueAsText
        ruido_modelo = params[5].valueAsText
        var_ruido = params[6].valueAsText
        media_aditivo = params[7].valueAsText
        media_multiplicativo = params[8].valueAsText
        nlooks = params[9].valueAsText
        factor_humedad = params[10].valueAsText

        mejoramiento_1_imagen = "Speckle_Imagenl.tif"
        mejoramiento_2_imagen = "Speckle_Imagen2.tif"

        ruta1 = os.path.join(carpeta_destino,mejoramiento_1_imagen)
        ruta2 = os.path.join(carpeta_destino,mejoramiento_2_imagen)

        """----------------------------APLIQUEMOS EL FILTRO---------------------------"""
        arcpy.AddMessage("Ejecutando la función Speckle ... ")

        if tipo_filtro == "Kuan":
            filtro_speckle_1 = arcpy.sa.Speckle(imagen_1_entrada,filter_type=tipo_filtro,filter_size=tamano_filtro,nlooks=nlooks)
            filtro_speckle_1.save(ruta1)
            arcpy.AddMessage("Filtro Speckle (Kuan) para la primera imagen aplicado con éxito")

            filtro_speckle_2 = arcpy.sa.Speckle(imagen_2_entrada, filter_type=tipo_filtro , filter_size=tamano_filtro, nlooks=nlooks)
            filtro_speckle_2.save(ruta2)
            arcpy.AddMessage("Filtro Speckle ( Kuan ) para la segunda imagen aplicado con éxito")

        elif tipo_filtro == "Lee":
            filtro_speckle_1 = arcpy.sa.Speckle(imagen_1_entrada,filter_type=tipo_filtro, filter_size=tamano_filtro,noise_model = ruido_modelo, noise_var=var_ruido,additive_noise_mean=media_aditivo, multiplicative_noise_mean=media_multiplicativo,nlooks=nlooks)
            filtro_speckle_1.save(ruta1)
            arcpy.AddMessage("Filtro Speckle (Lee) para la primera imagen aplicado con éxito")

            filtro_speckle_2 = arcpy.sa.Speckle(imagen_2_entrada,filter_type=tipo_filtro,filter_size=tamano_filtro,
                                      noise_model=ruido_modelo,noise_var=var_ruido,
                                      additive_noise_mean=media_aditivo, multiplicative_noise_mean=media_multiplicativo,
                                      nlooks=nlooks)
            arcpy.AddMessage("Filtro Speckle (Lee) para la segunda imagen aplicado con éxito")
            filtro_speckle_2.save(ruta2)

        elif tipo_filtro == "Lee Enriquecido":

            filtro_speckle_1 = arcpy.sa.Speckle(imagen_1_entrada,filter_type=tipo_filtro, filter_size=tamano_filtro,
                                      damp_factor=factor_humedad)
            filtro_speckle_1.save(ruta1)
            arcpy.AddMessage("Filtro Speckle (Lee Enriquecido) para la primera imagen aplicado con éxito")

            filtro_speckle_2 = arcpy.sa.Speckle(imagen_2_entrada, filter_type=tipo_filtro, filter_size=tamano_filtro,
                                      damp_factor= factor_humedad )
            filtro_speckle_2.save(ruta2)
            arcpy.AddMessage("Filtro Speckle (Lee Enriquecido) para la segunda imagen aplicado con éxito")

        elif tipo_filtro == "Frost":

            filtro_speckle_1 = arcpy.sa.Speckle(imagen_1_entrada, filter_type=tipo_filtro, filter_size=tamano_filtro,
                                  damp_factor=factor_humedad)
            filtro_speckle_1.save(ruta1)
            arcpy.AddMessage("Filtro Speckle (Frost) para la primera imagen aplicado con éxito")

            filtro_speckle_2 = arcpy.sa.Speckle(imagen_2_entrada, filter_type=tipo_filtro, filter_size=tamano_filtro,
                                  damp_factor=factor_humedad)
            filtro_speckle_2.save(ruta2)
            arcpy.AddMessage("Filtro Speckle (Frost) para la segunda imagen aplicado con éxito")

 

        """----------------------------DETECCION DE CAMBIOS---------------------------"""
        
        arcpy.AddMessage("Calculando la relación logaritmica entre las imágenes ...")

        logImagen_1 = Log10(filtro_speckle_1)
        arcpy.AddMessage("Logaritmo de la primera imagen calculado con éxito")

        logImagen_2 = Log10(filtro_speckle_2)
        arcpy.AddMessage("Logaritmo de la segunda imagen calculado con éxito")
        relacion = Minus(logImagen_1, logImagen_2)
        nombreRelacion = "RelacionLogaritmica.tif"
        rutaRelacion = os.path.join(carpeta_destino, nombreRelacion)
        relacion.save(rutaRelacion)
        
        arcpy.AddMessage("Relación logarítmica calculada con éxito")
        arcpy.AddMessage("Aplicando segmentación ... ")

        segmentacion = Threshold(relacion)
        nombreSegmentacion = "Segmentacion.tif"
        rutaSegmentacion = os.path.join(carpeta_destino, nombresegmentacion)
        segmentacion.save(rutaSegmentacion)
        arcpy.AddMessage("Segmentación con éxito")
    
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
