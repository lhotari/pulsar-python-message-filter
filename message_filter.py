from pulsar import Function

class MessageFilterFunction(Function):
    """
    A simple Pulsar Function that filters messages based on whether
    the message body/payload contains a specific string.
    """
    
    def __init__(self):
        pass
           
    def process(self, input, context):
        """
        Process each incoming message and forward it to another topic
        if it contains the specified string.
        """
        # Convert input to string if it's not already
        message = str(input)
        
        # Get the filter string and destination topic from user config
        filter_string = context.get_user_config_value("filterString")
        destination_topic = context.get_user_config_value("destinationTopic")
        
        if not destination_topic:
            context.get_logger().error("Destination topic not configured")
            return None

        # Get the input message id and topic name
        input_message_id = context.get_message_id()
        input_topic_name = context.get_current_message_topic_name()
        # define a function to ack the input message
        def ack_input_message():
            context.ack(input_message_id, input_topic_name)

        # Simple string contains check
        if filter_string in message:
            # Message contains the filter string, forward to destination topic

            # Define the ack callback function for the publish call
            def ack_callback(result, sent_msg_id):
                if str(result) == "Result.Ok":
                    context.get_logger().info(f"Message sent to {destination_topic} with id {sent_msg_id}")
                    ack_input_message()
                else:
                    context.get_logger().error(f"Failed to send message to {destination_topic} for {input_message_id}, result was {result}")

            # Publish the message to the destination topic, the ack callback will be called when 
            # the message is published successfully

            # Preserve message properties (headers) from the input message
            # add "message_filter_function_input_topic" to the properties as extra property
            message_conf = {"properties": {"message_filter_function_input_topic": context.get_current_message_topic_name(), **context.get_message_properties()},
                            "ordering_key": context.get_message_key(), # preserve the ordering key
                            "partition_key": context.get_partition_key(), # preserve the partition key
                            "event_timestamp": context.get_message_eventtime()} # preserve the event timestamp
            
            # Call publish with message_conf and ack_callback
            context.publish(destination_topic, message, message_conf=message_conf, callback=ack_callback)
            context.get_logger().info(f"Forwarding message to {destination_topic}")

        else:
            context.get_logger().info(f"Message doesn't contain '{filter_string}', skipping")
            ack_input_message()
            
        return None
    