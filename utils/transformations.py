from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QTransform, QIcon
from PyQt6.QtWidgets import QTableView, QSizePolicy, QHeaderView


def resize_table_view(table_view: QTableView):
    # Set size policy and scroll mode
    table_view.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    table_view.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)

    default_column_width = 200

    # Set column widths
    header = table_view.horizontalHeader()
    header.setDefaultSectionSize(default_column_width)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    # Calculate total width needed for all columns
    total_width = default_column_width * table_view.model().columnCount()
    total_width += table_view.frameWidth() * 2
    total_width += table_view.verticalHeader().width()

    table_view.setMaximumWidth(total_width)

    # Fit height to show all rows in preview
    def update_height():
        row_height = table_view.verticalHeader().defaultSectionSize()
        header_height = table_view.horizontalHeader().height()
        frame_height = table_view.frameWidth() * 2
        has_scroll_bar = table_view.horizontalScrollBar().isVisible()
        scroll_bar_height = table_view.horizontalScrollBar().height() if has_scroll_bar else 0

        total_height = header_height + (row_height * table_view.model().rowCount()) + frame_height + scroll_bar_height
        table_view.setFixedHeight(total_height)

    # Defer until event loop has a chance to lay out the table
    QtCore.QTimer.singleShot(0, update_height)

def load_flipped_inverted_icon(path: str, flip_horizontal: bool=False, flip_vertical: bool=False, invert: bool=False) -> QIcon:
    pixmap = QPixmap(path)

    # Convert to image and flip colors
    if invert:
        image = pixmap.toImage()
        image.invertPixels()
        pixmap = QPixmap.fromImage(image)

    # Apply flip with transformations
    transform = QTransform()
    transform.scale(-1 if flip_horizontal else 1, -1 if flip_vertical else 1)

    flipped_pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

    return QIcon(flipped_pixmap)
