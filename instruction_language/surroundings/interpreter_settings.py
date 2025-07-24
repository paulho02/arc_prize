
from typing import Hashable, Union


class GISManager:
    """
    (Global Interpreter Settings Manager)
    """
    _settings_register: dict[Union[int, str], dict] = {}
    # todo implement this 'singleton'-like behavior for other service classes
    _active_settings_id: Union[int, None] = None

    @staticmethod
    def set(setting_id: Hashable, settings: dict):
        """
        Set a global interpreter setting.
        """
        setting_id = hash(setting_id)

        GISManager._settings_register[setting_id] = settings

    @staticmethod
    def get(setting_id: Hashable):
        """
        Get a global interpreter setting.
        """
        setting_id = hash(setting_id)

        if setting_id not in GISManager._settings_register:
            raise ValueError(f"Setting '{setting_id}' does not exist.")
        return GISManager._settings_register[setting_id]

    # todo maybe convert the GISManager to a interpreter manager that can handle multiple interpreters and schedule their runs when multiple interpreters try to run simultaneously
    @staticmethod
    def interpreter_lock(interpreter: Hashable):
        """
        Locks the interpreter settings to the specified key so that no other interpreter can change the settings while this interpreter is running.
        """
        settings_id = hash(interpreter)

        if GISManager._active_settings_id is not None:
            raise RuntimeError(
                "Another interpreter is already running with active settings.")
        if settings_id not in GISManager._settings_register:
            raise ValueError(f"Settings '{settings_id}' does not exist.")
        GISManager._active_settings_id = settings_id

    @staticmethod
    def release_interpreter_lock(interpreter: Hashable):
        """
        Releases the interpreter lock for the specified interpreter.
        """
        settings_id = hash(interpreter)

        if GISManager._active_settings_id != settings_id:
            raise RuntimeError(
                "Cannot release lock for an interpreter that is not locked.")
        GISManager._active_settings_id = None

    @staticmethod
    def get_settings_setting(settings_id: Union[int, str], setting_key: str):
        """
        Get a specific setting from the global interpreter settings.
        @param settings_key: The key of the settings to retrieve the setting from. (Imagine it as a namespace.)
        @param setting_key: The key of the setting to retrieve. (Imagine it as a key in a dictionary.)
        """
        if settings_id not in GISManager._settings_register:
            raise ValueError(f"Settings '{settings_id}' does not exist.")
        settings = GISManager.get(settings_id)
        if setting_key not in settings:
            raise ValueError(
                f"Setting '{setting_key}' does not exist in settings '{settings_id}'.")
        return settings[setting_key]

    @staticmethod
    def get_setting(setting_key: str):
        """
        Returns the value of the specified setting key from the currently active settings.
        @param setting_key: The key of the setting to retrieve. (Imagine it as a key in a dictionary.)
        """
        if GISManager._active_settings_id is None:
            raise ValueError("No active settings key is set.")
        return GISManager.get_settings_setting(
            GISManager._active_settings_id, setting_key)


GISManager.set("default", {
    "max_loop_iterations": 5000,
})
