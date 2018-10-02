from __future__ import unicode_literals
import datetime


class ChangesMixin(object):
    """
    Model mixin
    ChangesMixin keeps track of changes for model instances.
    """
    def __init__(self, *args, **kwargs):
        super(ChangesMixin, self).__init__(*args, **kwargs)
        self._states = []
        self._save_state(new_instance=True)

    def _save_state(self, new_instance=False):
        self._states.append(self.current_state())
        if len(self._states) > 2:
            self._states.pop(0)

    def current_state(self):
        """
        Returns a ``field -> value`` dict of the current state of the instance.
        """
        field_names = set()
        [field_names.add(f.name) for f in self._meta.local_fields]
        [field_names.add(f.attname) for f in self._meta.local_fields]
        return dict([(field_name, getattr(self, field_name)) for field_name in field_names])

    def previous_state(self):
        """
        Returns a ``field -> value`` dict of the state of the instance after it
        was created, saved or deleted the previous time.
        """
        return self._states[0]

    def _changes(self, other, current):
        return dict([(key, {'from': was, 'to': current[key]}) for key, was in other.iteritems()
                     if was != current[key] and key != 'last_updated'])

    def _changes_str(self, other, current):
        return dict([(str(key), {'from': str(was), 'to': str(current[key])}) for key, was in other.iteritems()
                     if was != current[key] and key != 'last_updated'])

    def changes(self):
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the previous state to the current state.
        """
        changes = self._changes(self.previous_state(), self.current_state())
        return changes if changes != {} else None

    def changes_str(self):
        changes_str = self._changes_str(self.previous_state(), self.current_state())
        return changes_str if changes_str != {} else None

    def previous_instance(self):
        """
        Returns an instance of this model in its previous state.
        """
        return self.__class__(**self.previous_state())
