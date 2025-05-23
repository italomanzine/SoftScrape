import unittest
import logging
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from softscrape.logger import get_logger, ERROR_LOG_FILE_PATH, ERROR_LOG_DIR, LOG_DIR_PATH

class TestLogger(unittest.TestCase):

    def setUp(self):
        # Explicitly ensure the log directory exists before each test
        os.makedirs(ERROR_LOG_DIR, exist_ok=True)

        if os.path.exists(ERROR_LOG_FILE_PATH):
            os.remove(ERROR_LOG_FILE_PATH)
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close() 
            root_logger.removeHandler(handler)
        
        import softscrape.logger
        softscrape.logger._handlers_configured = False

    def tearDown(self):
        if os.path.exists(ERROR_LOG_FILE_PATH):
            os.remove(ERROR_LOG_FILE_PATH)
        
        if os.path.exists(ERROR_LOG_DIR) and not os.listdir(ERROR_LOG_DIR):
            try:
                os.rmdir(ERROR_LOG_DIR)
                # If ERROR_LOG_DIR is removed, check if its parent LOG_DIR_PATH is also empty
                if os.path.exists(LOG_DIR_PATH) and not os.listdir(LOG_DIR_PATH):
                    os.rmdir(LOG_DIR_PATH)
            except OSError as e:
                # print(f"Warning: Could not remove directory in tearDown: {e}")
                pass 
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        
        import softscrape.logger
        softscrape.logger._handlers_configured = False

    def _flush_loggers(self):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.flush()

    def test_get_logger_returns_logger_instance(self):
        logger = get_logger("TestLogger")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "TestLogger")

    def test_logger_has_console_handler(self):
        logger = get_logger("ConsoleTest")
        root_logger = logging.getLogger()
        self.assertTrue(any(isinstance(h, logging.StreamHandler) and h.stream == sys.stdout for h in root_logger.handlers))

    def test_logger_has_error_file_handler(self):
        logger = get_logger("FileTest")
        root_logger = logging.getLogger()
        self.assertTrue(any(isinstance(h, logging.FileHandler) and h.baseFilename == ERROR_LOG_FILE_PATH for h in root_logger.handlers))

    def test_error_log_file_created_on_error(self):
        logger = get_logger("ErrorLogCreationTest")
        # Ensure the file is not present from a previous state within this test method
        if os.path.exists(ERROR_LOG_FILE_PATH):
            os.remove(ERROR_LOG_FILE_PATH) 
        self.assertFalse(os.path.exists(ERROR_LOG_FILE_PATH))
        logger.error("This is a test error message.")
        self._flush_loggers()
        self.assertTrue(os.path.exists(ERROR_LOG_FILE_PATH), f"Log file {ERROR_LOG_FILE_PATH} was not created.")

    def test_error_message_written_to_file(self):
        logger = get_logger("ErrorMessageWriteTest")
        test_message = "This is a critical test error."
        logger.error(test_message)
        self._flush_loggers()
        self.assertTrue(os.path.exists(ERROR_LOG_FILE_PATH), f"Log file not found: {ERROR_LOG_FILE_PATH}")
        with open(ERROR_LOG_FILE_PATH, 'r') as f:
            log_content = f.read()
        self.assertIn(test_message, log_content)
        self.assertIn("ERROR", log_content)
        self.assertIn("ErrorMessageWriteTest", log_content)

    def test_info_message_not_written_to_error_file(self):
        logger = get_logger("InfoMessageTest")
        logger.info("This is an info message.")
        logger.error("Ensuring error log file exists for test.") 
        self._flush_loggers()
        self.assertTrue(os.path.exists(ERROR_LOG_FILE_PATH), f"Log file not found: {ERROR_LOG_FILE_PATH}")
        with open(ERROR_LOG_FILE_PATH, 'r') as f:
            log_content = f.read()
        self.assertNotIn("This is an info message.", log_content)

    def test_handlers_configured_once(self):
        import softscrape.logger
        self.assertFalse(softscrape.logger._handlers_configured)
        get_logger("TestOnce1")
        self.assertTrue(softscrape.logger._handlers_configured)
        
        root_logger = logging.getLogger()
        initial_handler_count = len(root_logger.handlers)
        get_logger("TestOnce2")
        self.assertEqual(len(root_logger.handlers), initial_handler_count)
        self.assertTrue(softscrape.logger._handlers_configured)
