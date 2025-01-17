from returns.pipeline import is_successful

from piri3.mapper import map_data


def test_creating_key_to_name():
    """Test that we can fetch key in dict."""
    input_data = {'key': 'test name'}
    config = {
        'name': 'root',
        'array': False,
        'attributes': [
            {
                'name': 'name',
                'mappings': [
                    {
                        'path': ['key'],
                    },
                ],
            },
        ],
    }

    assert map_data(
        input_data,
        config,
    ).unwrap() == {'name': 'test name'}


def test_array_true_but_no_loop_gives_array():
    """Test that we get an array if we set array = true in object."""
    input_data = {'key': 'test name'}
    config = {
        'name': 'root',
        'array': True,
        'attributes': [
            {
                'name': 'name',
                'mappings': [
                    {
                        'path': ['key'],
                    },
                ],
            },
        ],
    }

    assert map_data(
        input_data,
        config,
    ).unwrap() == [{'name': 'test name'}]


def test_missing_data_gives_nothing():
    """Test that we get an array if we set array = true in object."""
    input_data = {'key': 'test name'}
    config = {
        'name': 'root',
        'array': True,
        'attributes': [
            {
                'name': 'name',
                'mappings': [
                    {
                        'path': ['missing'],
                    },
                ],
            },
        ],
    }

    assert is_successful(map_data(
        input_data,
        config,
    ))


def test_missing_data_creates_no_object():
    """Test that if an object mapping result is empty we create now 'key'."""
    input_data = {'key': 'test name'}
    config = {
        'name': 'root',
        'array': True,
        'attributes': [
            {
                'name': 'an_attribute',
                'default': 'val',
            },
        ],
        'objects': [
            {
                'name': 'test',
                'array': False,
                'attributes': [
                    {
                        'name': 'name',
                        'mappings': [
                            {
                                'path': ['missing'],
                            },
                        ],
                    },
                ],
            },
        ],
    }

    expected_result = [{
        'an_attribute': 'val',
        'test': {'name': None}
    }]

    assert map_data(
        input_data,
        config,
    ).unwrap() == expected_result


def test_double_repeatable():
    """Test that we can map nested repeatable objects."""
    config = {
        'name': 'root',
        'array': True,
        'iterables': [
            {
                'alias': 'journals',
                'path': ['journals'],
            },
        ],
        'attributes': [
            {
                'name': 'journal_id',
                'mappings': [
                    {
                        'path': ['journals', 'journal', 'id'],
                    },
                ],
            },
        ],
        'objects': [
            {
                'name': 'invoices',
                'array': True,
                'iterables': [
                    {
                        'alias': 'invoices',
                        'path': ['journals', 'journal', 'invoices'],
                    },
                ],
                'attributes': [
                    {
                        'name': 'amount',
                        'mappings': [
                            {
                                'path': ['invoices', 'amount'],
                            },
                        ],
                    },
                ],
            },
        ],
    }
    input_data = {
        'journals': [
            {
                'journal': {
                    'id': 1,
                    'invoices': [{'amount': 1.1}, {'amount': 1.2}],
                },
            },
            {
                'journal': {
                    'id': 2,
                    'invoices': [{'amount': 1.3}, {'amount': 1.4}],
                },
            },
        ],
    }
    expected_result = [
        {
            'journal_id': 1,
            'invoices': [
                {'amount': 1.1},
                {'amount': 1.2},
            ],
        },
        {
            'journal_id': 2,
            'invoices': [
                {'amount': 1.3},
                {'amount': 1.4},
            ],
        },
    ]

    assert map_data(
        input_data,
        config,
    ).unwrap() == expected_result


def test_mapping_where_data_is_not_found():
    """Test that when we map and don't find data its okay."""
    config = {
        'name': 'root',
        'array': True,
        'iterables': [
            {
                'alias': 'journals',
                'path': ['journals'],
            },
        ],
        'attributes': [
            {
                'name': 'journal_id',
                'mappings': [
                    {
                        'path': ['journals', 'journal', 'id'],
                    },
                ],
            },
        ],
        'objects': [
            {
                'name': 'invoices',
                'array': True,
                'iterables': [
                    {
                        'alias': 'invoices',
                        'path': ['journals', 'journal', 'invoices'],
                    },
                ],
                'attributes': [
                    {
                        'name': 'amount',
                        'mappings': [
                            {
                                'path': ['invoices', 'amount'],
                            },
                        ],
                    },
                ],
            },
        ],
        'branching_objects': [
            {
                'name': 'extrafield',
                'array': True,
                'branching_attributes': [
                    [
                        {
                            'name': 'datavalue',
                            'mappings': [
                                {
                                    'path': ['extra', 'extra1'],
                                },
                            ],
                        },
                    ],
                ],
            },
        ],
    }
    input_data = {
        'journals': [
            {
                'journal': {
                    'id': 1,
                    'invoices': [{}, {'amount': 1.2}],
                },
            },
            {
                'journal': {
                    'id': 2,
                },
            },
        ],
    }

    expected_result = [
        {
            'journal_id': 1,
            'invoices': [
                {'amount': None},
                {'amount': 1.2}
            ],
            'extrafield': [
                {'datavalue': None}
            ]
        },
        {
            'journal_id': 2,
            'invoices': [
                {'amount': None}
            ],
            'extrafield': [
                {'datavalue': None}
            ]
        }
    ]

    assert map_data(
        input_data,
        config,
    ).unwrap() == expected_result


def test_most_features():
    """Test that we can fetch key in dict."""
    config = {
        'name': 'schema',
        'array': False,
        'attributes': [
            {
                'name': 'name',
                'mappings': [
                    {
                        'path': ['key'],
                        'if_statements': [
                            {
                                'condition': 'is',
                                'target': 'val1',
                                'then': None,
                            },
                        ],
                        'default': 'default',
                    },
                    {
                        'path': ['key2'],
                        'if_statements': [
                            {
                                'condition': 'is',
                                'target': 'val2',
                                'then': 'if',
                            },
                        ],
                    },
                ],
                'separator': '-',
                'if_statements': [
                    {
                        'condition': 'is',
                        'target': 'default-if',
                        'then': None,
                    },
                ],
                'default': 'default2',
            },
        ],
        'objects': [
            {
                'name': 'address',
                'array': False,
                'attributes': [
                    {
                        'name': 'address1',
                        'mappings': [
                            {
                                'path': ['a1'],
                            },
                        ],
                    },
                    {
                        'name': 'address2',
                        'mappings': [
                            {
                                'path': ['a2'],
                            },
                        ],
                    },
                ],
            },
            {
                'name': 'people',
                'array': True,
                'iterables': [
                    {
                        'alias': 'persons',
                        'path': ['persons'],
                    },
                ],
                'attributes': [
                    {
                        'name': 'firstname',
                        'mappings': [
                            {
                                'path': ['persons', 'name'],
                            },
                        ],
                    },
                ],
            },
        ],
        'branching_objects': [
            {
                'name': 'extrafield',
                'array': True,
                'branching_attributes': [
                    [
                        {
                            'name': 'dataname',
                            'default': 'one',
                        },
                        {
                            'name': 'datavalue',
                            'mappings': [
                                {
                                    'path': ['extra', 'extra1'],
                                },
                            ],
                        },
                    ],
                    [
                        {
                            'name': 'dataname',
                            'default': 'two',
                        },
                        {
                            'name': 'datavalue',
                            'mappings': [
                                {
                                    'path': ['extra', 'extra2'],
                                },
                            ],
                        },
                    ],
                ],
            },
        ],
    }
    input_data = {
        'key': 'val1',
        'key2': 'val2',
        'a1': 'a1',
        'a2': 'a2',
        'persons': [{'name': 'john'}, {'name': 'bob'}],
        'extra': {
            'extra1': 'extra1val',
            'extra2': 'extra2val',
        },
    }
    expected_result = {
        'name': 'default2',
        'address': {
            'address1': 'a1',
            'address2': 'a2',
        },
        'people': [
            {'firstname': 'john'},
            {'firstname': 'bob'},
        ],
        'extrafield': [
            {'dataname': 'one', 'datavalue': 'extra1val'},
            {'dataname': 'two', 'datavalue': 'extra2val'},
        ],
    }

    assert map_data(
        input_data,
        config,
    ).unwrap() == expected_result
