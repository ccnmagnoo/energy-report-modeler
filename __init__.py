"""Raíz del repositorio.

La aplicación web vive en ``app/``. El código y los datos del generador
original de notebooks permanecen en ``models/``, ``libs/`` y ``source/``.

Este archivo se mantiene sin efectos secundarios a propósito: la versión
anterior creaba un ``Project`` y consultaba la API de clima al importar el
paquete raíz, lo que rompía pruebas y herramientas de introspección.
"""
