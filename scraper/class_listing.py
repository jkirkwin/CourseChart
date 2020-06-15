'''Holds a representation of a class listing in the Kuali catalog'''

# TODO extend this to pull out more information

class ClassListing:
    '''Represents a listing in the academic calendar'''

    def __init__(self, name, code):
        '''Creates a ClassListing'''
        self.name = name
        self.code = code

    def get_name(self):
        '''Returns the course name'''
        return self.name

    def get_code(self):
        '''Returns the course code'''
        return self.code


def get_from_web_element(class_element):
    '''Converts a selenium web element into a ClassListing instance'''
    course_desc = class_element.find_element_by_tag_name('h2').text
    (course_code, course_name) = parse_course_description(course_desc)

    return ClassListing(course_name, course_code)


def parse_course_description(desc):
    '''Extracts the course code and name from the description.

    The description must be of the form "<Course Code> - <Course Name>"
    '''
    seperator_index = desc.index(' - ')
    code = desc[:seperator_index].strip() # TODO split this into dept code and course number
    name = desc[seperator_index + 2:].strip()
    return (code, name)
