"""
Label processors to run when registering collected labels in the label manager.
"""
from .process_labels import ProcessLabels
from .process_duplicate_labels import FindDuplicateLabels
from .process_transfer_labels import TransferLabels
from .process_order_labels import OrderLabels
from .process_content_labels import ProcessContentLabels
