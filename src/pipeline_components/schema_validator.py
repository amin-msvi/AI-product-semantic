from typing import Dict, List, Any
import re
import logging


class SchemaValidator:
    """Validates product data against AI schema requirements."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_product(self, product, schema):
        """
        Validate a single product against the schema.
        
        Args:
            product: Product dictionary to validate
            schema: Schema dictionary with validation rules
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        product_id = product.get('id', 'Unknown')
        
        # Validate required fields
        errors.extend(self._validate_required_fields(product, schema))
        
        # Validate field types and constraints
        errors.extend(self._validate_field_constraints(product, schema))
        
        if errors:
            self.logger.warning(f"Product {product_id} has {len(errors)} validation errors")
        else:
            self.logger.info(f"Product {product_id} passed validation")
        
        return errors
    
    def validate_batch(self, products, schema):
        """Validate multiple products against the schema."""
        validation_results = {}
        
        for product in products:
            product_id = product.get('id', f'Product_{len(validation_results)}')
            errors = self.validate_product(product, schema)
            
            if errors:
                validation_results[product_id] = errors
        
        self.logger.info(f"Validated {len(products)} products. "
                        f"{len(validation_results)} products have validation errors.")
        
        return validation_results
    
    def _validate_required_fields(self, product, schema):
        """Validate that all required fields are present."""
        errors = []
        required_fields = schema.get('required_fields', {})
        
        for field_name in required_fields.keys():
            if field_name not in product:
                errors.append(f"Missing required field: {field_name}")
            elif product[field_name] is None or product[field_name] == '':
                errors.append(f"Required field '{field_name}' is empty")
        
        return errors
    
    def _validate_field_constraints(self, product, schema):
        """Validate field types and constraints."""
        errors = []
        
        # Validate required fields
        for field_name, rule in schema.get('required_fields', {}).items():
            if field_name in product:
                field_errors = self._validate_field_rule(product[field_name], rule, field_name)
                errors.extend(field_errors)
        
        # Validate optional fields if present
        for field_name, rule in schema.get('optional_fields', {}).items():
            if field_name in product and product[field_name]:
                field_errors = self._validate_field_rule(product[field_name], rule, field_name)
                errors.extend(field_errors)
        
        return errors
    
    def _validate_field_rule(self, value: Any, rule, field_name):
        """Validate a single field against its rule."""
        errors = []
        rule_lower = rule.lower()
        
        # String validation
        if 'string' in rule_lower:
            if not isinstance(value, str):
                errors.append(f"Field '{field_name}' should be string, got {type(value).__name__}")
            else:
                # Check max length constraints
                max_length = self._extract_max_length(rule)
                if max_length and len(value) > max_length:
                    errors.append(f"Field '{field_name}' exceeds max length of {max_length} characters")
        
        # Float/numeric validation
        elif 'float' in rule_lower:
            if not isinstance(value, (int, float)):
                errors.append(f"Field '{field_name}' should be numeric, got {type(value).__name__}")
            elif '>0' in rule and float(value) <= 0:
                errors.append(f"Field '{field_name}' should be greater than 0")
        
        # Enum validation
        elif 'enum' in rule_lower:
            allowed_values = self._extract_enum_values(rule)
            if allowed_values and value not in allowed_values:
                errors.append(f"Field '{field_name}' has invalid value '{value}'. "
                            f"Allowed values: {', '.join(allowed_values)}")
        
        # URL validation
        elif 'url' in rule_lower:
            if value and not self._is_valid_url(value):
                errors.append(f"Field '{field_name}' should be a valid URL")
        
        return errors
    
    def _extract_max_length(self, rule):
        """Extract maximum length from rule string."""
        match = re.search(r'max (\d+) chars', rule)
        if match:
            return int(match.group(1))
        return 0
    
    def _extract_enum_values(self, rule):
        """Extract enum values from rule string."""
        match = re.search(r'enum\[(.*?)\]', rule)
        if match:
            values = match.group(1).split(',')
            return [v.strip() for v in values]
        return []
    
    def _is_valid_url(self, url):
        """Basic URL validation."""
        if not url:
            return True  # Empty URLs are allowed for optional fields
        
        return (url.startswith('http://') or 
                url.startswith('https://') or 
                url.startswith('www.'))
    
    def get_validation_summary(self, validation_results):
        """Generate a human-readable validation summary."""
        if not validation_results:
            return "All products passed validation successfully!"
        
        total_errors = sum(len(errors) for errors in validation_results.values())
        
        summary_lines = [
            f"Validation found {total_errors} errors in {len(validation_results)} products:",
            ""
        ]
        
        for product_id, errors in validation_results.items():
            summary_lines.append(f"Product {product_id}:")
            for error in errors:
                summary_lines.append(f"  . {error}")
            summary_lines.append("")
        
        return "\n".join(summary_lines)
