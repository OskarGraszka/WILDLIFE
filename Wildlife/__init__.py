# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Wildlife
                                 A QGIS plugin
 This plugin helps to store wildlife observations.
                             -------------------
        begin                : 2017-11-11
        copyright            : (C) 2017 by PRYZMAP
        email                : biuro@pryzmap.pl
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Wildlife class from file Wildlife.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Wildlife import Wildlife
    return Wildlife(iface)
