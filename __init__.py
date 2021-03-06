# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VixedRequests
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Mikhail Itkin/NPOLAR'
__date__ = '2021-04-24'
__copyright__ = '(C) 2021 by Mikhail Itkin/NPOLAR'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load VixedRequests class from file VixedRequests.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .vixed_request import VixedRequestsPlugin
    return VixedRequestsPlugin(iface)
