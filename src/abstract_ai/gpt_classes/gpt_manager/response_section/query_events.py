from ..dependencies import *
def query_event_check(self) -> bool:
    if self.event == "-SUBMIT_QUERY-":
        if not self.submission_in_progress:
            self.submission_in_progress = True
            self.get_new_api_call_name()
            # Submit the coroutine to the event loop
            future = asyncio.run_coroutine_threadsafe(self.submit_query(), self.loop)
            # Optionally, handle the result or exceptions
            future.add_done_callback(self.handle_future_result)
        else:
            self.logger.info("Submission already in progress.")
        self.event = None
    else:
        return False
    return True

def handle_future_result(self, future):
    result = future.result()
    #try:
        
        # Process the result if needed
    #except Exception as e:
    #    self.logger.error(f"Error in async task: {e}")
def submit_event(self):
    logger.info(f"submit_event..")
    self.get_new_api_call_name()
    self.start_query = False
    self.updated_progress = False
    self.response_mgr.re_initialize_query()
    asyncio.run(self.submit_query())
    self.submission_in_progress = False  # Reset the flag when done
async def submit_query(self) -> None:
    logger.info(f"submit_query..")
    try:
        # Update the GUI components from the main thread using a thread-safe method
        self.window.write_event_value('-DISABLE_SUBMIT_BUTTON-', True)

        self.dots = '...'
        self.start_query = False
        if self.test_bool:
            self.latest_output = [safe_read_from_json(self.test_file_path)]
        else:
            self.latest_output = await self.get_query() or []
        self.output_list.append(self.latest_output)
        self.logger.info(f"recent output_list: {self.output_list}")
        self.update_progress_chunks(done=True)
        self.update_last_response_file()
        self.update_text_with_responses()
        # Re-enable the submit button
        self.window.write_event_value('-ENABLE_SUBMIT_BUTTON-', True)
        if not self.window_mgr.get_values()['-REUSE_CHUNK_DATA-']:
            self.update_prompt_data('')
        self.response = False
    finally:
        self.submission_in_progress = False
    
    
async def get_query(self) -> None:
    logger.info(f"get_query..")
    self.response = await self.response_mgr.initial_query()
    return self.response
