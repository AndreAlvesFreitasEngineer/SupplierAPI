from enum import Enum


class ContractStatus(str, Enum):
    """
    Represents the current state of a contract.
    """

    PENDING = "pending"  # Contract is drafted but not yet active
    ACTIVE = "active"  # Contract is in effect and valid
    COMPLETED = "completed"  # Contract has been fulfilled
    CANCELLED = "cancelled"  # Contract was cancelled before completion


class CargoStatus(str, Enum):
    """
    Represents the lifecycle stage of cargo.
    """

    PENDING = "pending"  # Cargo is planned or scheduled
    IN_TRANSIT = "in_transit"  # Cargo is currently being transported
    DELIVERED = "delivered"  # Cargo has reached its final destination


class VesselStatus(str, Enum):
    """
    Indicates the operational status of a vessel.
    """

    ACTIVE = "active"  # Vessel is operational and available
    MAINTENANCE = "maintenance"  # Vessel is undergoing maintenance
    INACTIVE = "inactive"  # Vessel is out of service or decommissioned


class TrackingStatus(str, Enum):
    """
    Describes the current status in the cargo's tracking journey.
    """

    LOADING = "loading"  # Cargo is being loaded onto the vessel
    IN_TRANSIT = "in_transit"  # Cargo is en route to destination
    UNLOADING = "unloading"  # Cargo is being offloaded from the vessel
    DELIVERED = "delivered"  # Cargo has been successfully delivered
