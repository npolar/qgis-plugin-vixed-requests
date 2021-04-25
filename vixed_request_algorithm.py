# -*- coding: utf-8 -*-

"""
/***************************************************************************
 VixedTest
                                 A QGIS plugin
 Sample description
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-04-24
        copyright            : (C) 2021 by Mikhail Itkin/NPOLAR
        email                : user@example.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Mikhail Itkin/NPOLAR'
__date__ = '2021-04-24'
__copyright__ = '(C) 2021 by Mikhail Itkin/NPOLAR'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import json

from qgis.utils import iface
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProject,
    QgsProcessing,
    QgsProcessingParameterEnum,
    QgsProcessingParameterExtent,
    QgsProcessingAlgorithm,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterString,
    QgsProcessingParameterDateTime,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem
    )


class VixedTestAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    SEND_TO = "SEND_TO"
    EXTENT = 'EXTENT'
    OPTIONS = 'OPTIONS'
    PROCESSORS = "PROCESSORS"
    ESTIMATED_FILESIZE = "Estimated filesize"
    RESOLUTION = 'RESOLUTION'
    TIMEDELTA = 'TIMEDELTA'
    RECIPIENTS = "RECIPIENTS"
    EXPORTCRS = "epsg:32633"
    CRS = "CRS"
    END_DATE = "END_DATE"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.BASEDIR, self.FILENAME = os.path.split(os.path.abspath(__file__))

        processors = [
            self.tr("SAR"),
            self.tr("CHLA")
        ]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.PROCESSORS,
                self.tr("Vixed Processors"),
                options=processors, defaultValue='SAR'
            )
        )

        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Select extent')
            )
        )

        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT,
                self.tr('Select extent')
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.RESOLUTION,
                self.tr(
                    'Spatial resolution (meters per pixel)'),
                defaultValue=300,
                minValue=50,
                type=QgsProcessingParameterNumber.Integer
        ))

        self.addParameter(QgsProcessingParameterNumber(
            self.TIMEDELTA,
            self.tr(
                'Temporal aggregation window (hours)'),
            defaultValue=24,
            minValue=1,
            type=QgsProcessingParameterNumber.Integer
        ))

        self.addParameter(QgsProcessingParameterDateTime(
            self.END_DATE,
            self.tr("[optional] End date/time boundary for searching past data")
        ))

        try:
            with open(os.path.join(self.BASEDIR, 'tempdata'), mode='r') as tf:
                temp_dict = json.loads(tf.read())
                default_recipient = temp_dict['send_to']
        except:
            default_recipient = "user@example.com" 

        default_recipient = "user@example.com"

        self.addParameter(QgsProcessingParameterString(
            self.RECIPIENTS,
            self.tr('Send to email address'),
            defaultValue = default_recipient,
            multiLine = False

        ))

        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT,
            self.tr('Output request file (JSON)'),
            self.tr('JSON files (*.json)')
        ))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        self.CRS = iface.mapCanvas().mapSettings().destinationCrs().authid()
        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        crs_dst = QgsCoordinateReferenceSystem("EPSG:4326")
        crs_src = QgsCoordinateReferenceSystem(QgsProject.instance().crs())
        geo2proj = QgsCoordinateTransform(crs_src, crs_dst, QgsProject.instance())
        extent_proj = geo2proj.transform(extent)
        

        with open(os.path.join(self.BASEDIR, 'request_template.json'), mode='r') as json_template_fh:
            template_dict = json.load(json_template_fh)

        output = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        send_to = self.parameterAsString(parameters, self.RECIPIENTS, context)
        
        resolution = self.parameterAsInt(parameters, self.RESOLUTION, context)
        end_date = self.parameterAsDateTime(parameters, self.END_DATE, context).toString("yyyy-MM-ddTHH:mm:ssZ")

        template_dict['processor_settings']['spatial_resolution'] = resolution
        template_dict['processor_settings']['time_delta_hours'] = self.parameterAsInt(parameters, self.TIMEDELTA, context)
        template_dict['processor_settings']['roi'] =  self.wktPolygonToDict(extent_proj) # extent_proj.asWktPolygon()
        template_dict['processor_settings']['crs'] = self.EXPORTCRS
        template_dict['processor_settings']['end_date'] = end_date
        template_dict['send_to'] = [ send_to ]


        with open(os.path.join(self.BASEDIR, 'tempdata'), mode='w') as tf:
            json.dump({"send_to": send_to}, tf)
        
        with open(output, mode="w") as output_json:
            json.dump(template_dict, output_json, indent=2)

        filesize =  self.calcFileSize(extent, resolution)

        return {
            "OUTPUT": output,
            "ESTIMATED_FILESIZE": "{:0.2f} MB".format(filesize),
            "CRS": self.CRS,
            "EXTENT": extent_proj,
            "END_DATE": end_date
        }
        

    # def name(self):
    #     """
    #     Returns the algorithm name, used for identifying the algorithm. This
    #     string should be fixed for the algorithm, and must not be localised.
    #     The name should be unique within each provider. Names should contain
    #     lowercase alphanumeric characters only and no spaces or other
    #     formatting characters.
    #     """
    #     return 'Generate SAR request form'

    # def displayName(self):
    #     """
    #     Returns the translated algorithm name, which should be used for any
    #     user-visible display of the algorithm name.
    #     """
    #     return self.tr(self.name())

    # def group(self):
    #     """
    #     Returns the name of the group this algorithm belongs to. This string
    #     should be localised.
    #     """
    #     return self.tr(self.groupId())

    # def groupId(self):
    #     """
    #     Returns the unique ID of the group this algorithm belongs to. This
    #     string should be fixed for the algorithm, and must not be localised.
    #     The group id should be unique within each provider. Group id should
    #     contain lowercase alphanumeric characters only and no spaces or other
    #     formatting characters.
    #     """
    #     return ''

    # def tr(self, string):
    #     return QCoreApplication.translate('Processing', string)


    # def createInstance(self):
    #     return VixedRequestsAlgorithm()


    def wktPolygonToDict(self, extent):
        
        if self.CRS.upper() != "EPSG:4326":
            xmin, ymin = (extent.xMinimum(), extent.yMinimum())
            xmax, ymax = (extent.xMaximum(), extent.yMaximum())

        polygon = { "coordinates" : [
            [
            [xmin, ymin],
            [xmax, ymin],
            [xmax, ymax],
            [xmin, ymax],
            [xmin, ymin]
            ]
        ], "type": "Polygon" }
        
        return polygon
    
    def calcFileSize(self, extent, resolution, compression_ratio=100, channels_no=1):

        if self.CRS.upper() == "EPSG:4326":
            # pr = Proj(init="EPSG:32633")
            pr = None
            xmin, ymin = pr(extent.xMinimum(), extent.yMinimum())
            xmax, ymax = pr(extent.xMaximum(), extent.yMaximum())
        else:
            xmin, ymin = (extent.xMinimum(), extent.yMinimum())
            xmax, ymax = (extent.xMaximum(), extent.yMaximum())

        width  = xmax - xmin
        height = ymax - ymin
        area = width * height
        filesize = (area / (float(resolution) ** 2) ) * 8 / 1e6 / (compression_ratio / channels_no)

        return filesize


    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Generate request offline'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Vixed Requests'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return VixedTestAlgorithm()


class VixedOnlineAlgorithm(VixedTestAlgorithm):
    def name(self):
        return "Submit request directly (online)"

