import os

def generate_draugr_command(
    server,
    run_folder, 
    order_list, 
    disable_wizard=False, 
    is_multiome=False, 
    bcl_flags=None, 
    cellranger_flags=None, 
    bases2fastq_flags=None,
    advanced_options=[]
):
    """
    Generate a command string for the Draugr pipeline.

    Args:
        server (str): Server location
        run_folder (str): Run folder name.
        order_list (list): List of order IDs to process.
        disable_wizard (bool): Disable the wizard.
        is_multiome (bool): Enable multiome mode.
        bcl_flags (str): Custom Bcl2fastq flags.
        cellranger_flags (str): Custom Cellranger flags.
        bases2fastq_flags (str): Custom Bases2fastq flags.
        advanced_options (list): Additional advanced options for the command.

    Returns:
        str: Command string for the Draugr pipeline.
    """

    run_folder = run_folder.lstrip('/')

    draugr_command = (
    f"python {os.path.join('/export', 'local', 'analyses', 'draugr_exec', 'draugr.py')}"
    f" --login-config {os.path.join('/home', 'illumina', 'bfabric_cred', '.bfabricpy.yml')}"
    f" --run-folder {os.path.join('/export', 'local', 'data', run_folder)}"
    f" --analysis-folder {os.path.join('/export', 'local', 'analyses')}"
    f" --logger-rep {os.path.join('/srv', 'GT', 'analysis', 'falkonoe', 'dmx_logs', 'prod')}"
    f" --scripts-destination {os.path.join('/srv', 'GT', 'analysis', 'datasets')}"
    )

    if disable_wizard:
        draugr_command += " --disable-wizard"
    if is_multiome:
        draugr_command += " --is-multiome-run"
    if bcl_flags:
        draugr_command += " --custom-bcl2fastq-flags " + bcl_flags
    if cellranger_flags:
        draugr_command += " --custom-cellranger-flags " + cellranger_flags
    if bases2fastq_flags:
        draugr_command += " --custom-bases2fastq_flags " + bases2fastq_flags
    
    draugr_command += " --reprocess-orders " + ",".join([str(elt) for elt in order_list])

    SET_ENVIRON = "export OPENBLAS_NUM_THREADS=1 && export OPENBLAS_MAIN_FREE=1 &&"
    LMOD_PROFILE = os.path.join("/usr", "local", "ngseq", "etc", "lmod_profile")
    MODULE_PATH = os.path.join("/usr", "local", "ngseq", "etc", "modules")
    LMOD_SETUP = f"source {LMOD_PROFILE} && export MODULEPATH={MODULE_PATH} &&"
    # CONDA_SETUP = ". /usr/local/ngseq/miniconda3/etc/profile.d/conda.sh && conda activate gi_py3.11.5 &&"
    CONDA_SETUP = "module load Dev/Python && conda activate gi_py3.11.5 &&"
    MODULE_LOAD = "module load Tools/bcl2fastq && module load Aligner/CellRanger && module load Aligner/CellRangerARC && module load Tools/Bases2Fastq"

    PREFIX = f"{SET_ENVIRON} {LMOD_SETUP} {CONDA_SETUP} {MODULE_LOAD}"

    system_call = f"{PREFIX} && {draugr_command} "

    if advanced_options:
        system_call += " " + " ".join(advanced_options)

    # return system_call
    return system_call