from uuid import uuid4
from datetime import datetime

from pynwb import NWBFile
from pynwb.file import Subject, ProcessingModule
import pytest

from nwbinspector import InspectorMessage, Importance
from nwbinspector.checks.nwbfile_metadata import (
    check_experimenter,
    check_experiment_description,
    check_institution,
    check_subject_sex,
    check_subject_age,
    check_subject_species,
    check_subject_exists,
    check_subject_id_exists,
    check_processing_module_name,
    check_session_start_time,
    check_timestamps_reference_time,
    PROCESSING_MODULE_CONFIG,
)
from nwbinspector.register_checks import Severity
from nwbinspector.tools import make_minimal_nwbfile


minimal_nwbfile = make_minimal_nwbfile()


def test_check_session_start_time_pass():
    assert check_session_start_time(minimal_nwbfile) is None


def test_check_session_start_time_fail():
    nwbfile = NWBFile(session_description="", identifier=str(uuid4()), session_start_time=datetime(1960, 1, 1))
    assert check_session_start_time(nwbfile) == InspectorMessage(
        message="The session_start_time may not be set to the true date of the recording.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_session_start_time",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_check_timestamps_reference_time_pass():
    assert check_timestamps_reference_time(minimal_nwbfile) is None


def test_check_check_timestamps_reference_time_fail():
    nwbfile = NWBFile(
        session_description="",
        identifier=str(uuid4()),
        session_start_time=datetime.now().astimezone(),
        timestamps_reference_time=datetime(1960, 1, 1).astimezone(),
    )
    assert check_timestamps_reference_time(nwbfile) == InspectorMessage(
        message="The timestamps_reference_time may not be set to the true date of the recording.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_timestamps_reference_time",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_experimenter():
    assert check_experimenter(minimal_nwbfile) == InspectorMessage(
        message="Experimenter is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_experimenter",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_experiment_description():
    assert check_experiment_description(minimal_nwbfile) == InspectorMessage(
        message="Experiment description is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_experiment_description",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_check_institution():
    assert check_institution(minimal_nwbfile) == InspectorMessage(
        message="Metadata /general/institution is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_institution",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


@pytest.mark.skip(reason="TODO")
def test_check_keywords():
    pass


@pytest.mark.skip(reason="TODO")
def test_check_doi_publications():
    pass


def test_check_subject_sex():

    nwbfile = NWBFile(session_description="", identifier=str(uuid4()), session_start_time=datetime.now().astimezone())
    nwbfile.subject = Subject(subject_id="001")

    assert check_subject_sex(nwbfile.subject) == InspectorMessage(
        message="Subject.sex is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_sex",
        object_type="Subject",
        object_name="subject",
        location="",
    )


def test_check_subject_sex_other_value():
    subject = Subject(subject_id="001", sex="Male")

    assert check_subject_sex(subject) == InspectorMessage(
        message="Subject.sex should be one of: 'M' (male), 'F' (female), 'O' (other), or 'U' (unknown).",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_sex",
        object_type="Subject",
        object_name="subject",
        location="/",
    )


def test_check_subject_age_missing():
    subject = Subject(subject_id="001", sex="Male")
    assert check_subject_age(subject) == InspectorMessage(
        message="Subject is missing age and date_of_birth.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_age",
        object_type="Subject",
        object_name="subject",
        location="/",
    )


def test_check_subject_species():
    subject = Subject(subject_id="001")
    assert check_subject_species(subject) == InspectorMessage(
        message="Subject species is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_species",
        object_type="Subject",
        object_name="subject",
        location="/",
    )


def test_check_subject_age_iso8601():
    subject = Subject(subject_id="001", sex="Male", age="9 months")
    assert check_subject_age(subject) == InspectorMessage(
        message="Subject age does not follow ISO 8601 duration format, e.g. 'P2Y' for 2 years or 'P23W' for 23 "
        "weeks.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_age",
        object_type="Subject",
        object_name="subject",
        location="/",
    )


def test_pass_check_subject_age_with_dob():
    subject = Subject(subject_id="001", sex="Male", date_of_birth=datetime.now())
    assert check_subject_age(subject) is None


def test_check_subject_species_not_iso8601():
    subject = Subject(subject_id="001", species="Human")

    assert check_subject_species(subject) == InspectorMessage(
        message="Species should be in latin binomial form, e.g. 'Mus musculus' and 'Homo sapiens'",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_species",
        object_type="Subject",
        object_name="subject",
        location="/",
    )


def test_pass_check_subject_age():
    subject = Subject(subject_id="001", sex="Male", age="P9M")
    assert check_subject_age(subject) is None


def test_check_subject_exists():
    assert check_subject_exists(minimal_nwbfile) == InspectorMessage(
        message="Subject is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_exists",
        object_type="NWBFile",
        object_name="root",
        location="/",
    )


def test_pass_check_subject_exists():
    nwbfile = NWBFile(session_description="", identifier=str(uuid4()), session_start_time=datetime.now().astimezone())
    nwbfile.subject = Subject(subject_id="001", sex="Male")
    assert check_subject_exists(nwbfile) is None


def test_check_subject_id_exists():
    subject = Subject(sex="Male")
    assert check_subject_id_exists(subject) == InspectorMessage(
        message="subject_id is missing.",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_subject_id_exists",
        object_type="Subject",
        object_name="subject",
        location="/",
    )


def test_pass_check_subject_species():
    subject = Subject(subject_id="001", species="Homo sapiens")
    assert check_subject_species(subject) is None


def test_pass_check_subject_id_exist():
    subject = Subject(subject_id="001", sex="Male")
    assert check_subject_id_exists(subject) is None


def test_check_processing_module_name():
    processing_module = ProcessingModule("test", "desc")
    assert check_processing_module_name(processing_module) == InspectorMessage(
        message=f"Processing module is named test. It is recommended to use the schema "
        f"module names: {', '.join(PROCESSING_MODULE_CONFIG)}",
        importance=Importance.BEST_PRACTICE_SUGGESTION,
        check_function_name="check_processing_module_name",
        object_type="ProcessingModule",
        object_name="test",
        location="/",
    )


def test_pass_check_processing_module_name():
    processing_module = ProcessingModule("ecephys", "desc")
    assert check_processing_module_name(processing_module) is None


@pytest.mark.skip(reason="TODO")
def test_check_subject_species():
    pass
